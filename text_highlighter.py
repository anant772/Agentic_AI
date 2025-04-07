import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QFileDialog, QTextEdit,
                            QLabel, QScrollArea, QSplitter, QListWidget)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat

class NativePDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Native PDF Viewer")
        self.setGeometry(100, 100, 1024, 768)
        
        # Main widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        
        self.btn_open = QPushButton("Open PDF")
        self.btn_extract = QPushButton("Get Selected Text")
        self.page_label = QLabel("Page: 1")

        self.btn_PDF_extract = QPushButton("📝 Extract Text")
        self.btn_PDF_extract.setFixedWidth(100)
        self.btn_PDF_extract.clicked.connect(self.extract_text)
        toolbar_layout.addWidget(self.btn_PDF_extract)
        
        toolbar_layout.addWidget(self.btn_open)
        toolbar_layout.addWidget(self.btn_extract)
        toolbar_layout.addWidget(self.page_label)
        toolbar_layout.addStretch()
         
        # PDF Display Area (using QTextEdit for native text handling)
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidget(self.text_area)
        scroll.setWidgetResizable(True)

        # Create a widget for the occurrences list
        splitter = QSplitter(Qt.Horizontal)
        occurrence_widget = QWidget()
        occurrence_layout = QVBoxLayout(occurrence_widget)
        self.occurrence_label = QLabel("Occurrences:")
        self.occurrence_list = QListWidget()
        occurrence_layout.addWidget(self.occurrence_label)
        occurrence_layout.addWidget(self.occurrence_list)

        # Add widgets to splitter
        splitter.addWidget(occurrence_widget)
        splitter.addWidget(scroll)  # 'scroll' contains the QTextEdit (self.text_area)
        
        layout.addWidget(toolbar)
        layout.addWidget(scroll)
        layout.addWidget(splitter)
        
        # PDF document state
        self.doc = None
        self.current_page = 0
        
        # Connect signals
        self.btn_open.clicked.connect(self.open_pdf)
        self.btn_extract.clicked.connect(self.get_selected_text)
    
    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF", "", "PDF Files (*.pdf)")
        
        if file_path:
            self.doc = fitz.open(file_path)
            self.display_page(0)
    
    def display_page(self, page_num):
        if not self.doc or page_num < 0 or page_num >= len(self.doc):
            return
            
        self.current_page = page_num
        page = self.doc.load_page(page_num)
        
        # Extract text with formatting and layout information
        blocks = page.get_text("blocks")
        
        # Display text while preserving layout
        self.text_area.clear()
        cursor = self.text_area.textCursor()

        highlight_texts = getattr(self, 'similarContent', None)
        full_Text = getattr(self, 'full_text', None)

        def normalize_text(text):
            # Replace smart quotes and normalize whitespace
            return ' '.join(text.replace('’', "'").split())

        for block in sorted(blocks, key=lambda b: (b[1], b[0])):
            x0, y0, x1, y1, text, block_no, block_type = block
            if block_type == 0:  # Text block
                if highlight_texts and isinstance(highlight_texts, list):
                    text_lower = normalize_text(text).lower()
                    start_pos = 0
                    
                    while start_pos < len(text):
                        earliest_pos = len(text)
                        matched_text = None
                        matched_len = 0
                        
                        # Check each highlight string for a partial match
                        for highlight_text in highlight_texts:
                            highlight_lower = normalize_text(highlight_text).lower()
                            # Split highlight text into words and look for any match
                            pos = text_lower.find(highlight_lower, start_pos)
                            if pos != -1 and pos < earliest_pos:
                                earliest_pos = pos
                                matched_text = text[pos:pos + len(highlight_lower)]  # Use original text for display
                                matched_len = len(highlight_lower)
                        
                        if matched_text is None:  # No more matches
                            cursor.insertText(text[start_pos:] + "\n")
                            break
                        
                        # Insert text before the match
                        if earliest_pos > start_pos:
                            cursor.insertText(text[start_pos:earliest_pos])
                        
                        # Highlight the matched portion
                        highlight_format = QTextCharFormat()
                        highlight_format.setBackground(QColor("yellow"))
                        cursor.insertText(matched_text, highlight_format)
                        
                        # Reset to default format
                        default_format = QTextCharFormat()
                        cursor.setCharFormat(default_format)
                        
                        # Move past this match
                        start_pos = earliest_pos + matched_len
                else:
                    cursor.insertText(text + "\n")
        
        self.page_label.setText(f"Page: {page_num + 1}/{len(self.doc)}")
    
    def get_selected_text(self):
        cursor = self.text_area.textCursor()
        selected_text = cursor.selectedText()
        if selected_text.strip():
            print("\n=== SELECTED TEXT ===")
            print(selected_text.strip())
            print("=====================\n")
        else:
            print("No text selected!")
            return
        self.full_text = self.extract_text()
        self.occurrence_list.clear()
        self.similarContent = self.get_similar_content(selected_text, self.full_text)

        self.occurrence_label.setText(f"Contents related to '{selected_text}':")
        self.occurrence_list.addItem(self.similarContent.raw)
        self.similarContent = self.similarContent.raw.split("\n")
        # self.similarContent = ['The most semantically similar content from PDF chunks related to the phrase "Enhance Documents" is:', 'With the new Smallpdf experience, you can freely upload, organize, and share digital documents. When you enable the ‘Storage’ option, we’ll also store all processed files here. You can access files stored on Smallpdf from your computer, phone, or tablet. We’ll also sync files from the Smallpdf Mobile App to our online portal', 'When you right-click on a file, we’ll present you with an array of options to convert, compress, or modify it.']
        self.similarContent = list(filter(None, self.similarContent))
        self.similarContent = self.break_long_strings(self.similarContent)
        print(self.similarContent)


    
        self.display_page(self.current_page)




    def break_long_strings(self, string_list, max_length=60):
        result = []

        for text in string_list:

            ' '.join(text.replace('’', "'").split())

            if len(text) <= 5:
                continue  # Skip short strings

            if len(text) <= max_length:
                result.append(text)
                continue

            words = text.split()
            line = ""
            lines = []

            for word in words:
                if len(line) + len(word) + 1 <= max_length:
                    line += (" " if line else "") + word
                else:
                    lines.append(line)
                    line = word

            if line:
                # Avoid last tiny word on a new line if possible
                if len(line.split()) == 1 and lines:
                    if len(lines[-1]) + len(line) + 1 <= max_length:
                        lines[-1] += " " + line
                    else:
                        lines.append(line)
                else:
                    lines.append(line)

            result.extend(lines)

        return result
        


    def get_similar_content(self, selected_text, full_text):
        import os
        import json
        from crewai import LLM, Crew, Agent, Task

        os.environ["GROQ_API_KEY"] = "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"

        llm = LLM(
            model="groq/llama3-8b-8192",
            temperature=0.7
        )

        # Find Similar Content Agent
        similarity_analyzer = Agent(
            name="Jira Analyzer",
            role="Similarity Analyzer",
            goal="Find the most semantically similar content from PDF chunks",
            backstory=(
                "You're an expert at understanding sentence meaning and comparing text using semantic similarity."
                " Given a list of text chunks and a query, return the most relevant chunk(s) based on meaning."
            ),
            verbose=True,
            llm= llm
        )

        # Define Tasks
        analyze_similarity_task = Task(
            name="Find Similar Content",
            agent=similarity_analyzer,
            description=f"Find the most semantically similar content from PDF chunks - {full_text} which is related to this phrase -  \n{selected_text}",
            expected_output="Chunk(s) of text extracted from the PDF which are semantically similar to the given text",
            output_file='local/analyze_jira_test.txt'
        )

        # Crew AI Team
        crew = Crew(
            agents=[similarity_analyzer, ],
            tasks=[analyze_similarity_task, ]
        )

        # Run Crew
        results = crew.kickoff()
        return results

    def extract_text(self):
        if not hasattr(self, 'doc') or not self.doc:
            print("No PDF file loaded!")
            return
        
        try:
            doc = fitz.open(self.doc)
            full_text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                full_text += f"\n=== Page {page_num + 1} ===\n"
                full_text += page.get_text("text") + "\n"
            
            print(full_text)
            doc.close()
            return full_text
        except Exception as e:
            print(f"Error extracting text: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = NativePDFViewer()
    viewer.show()
    sys.exit(app.exec_())