
from fpdf import FPDF
import datetime

class PDF(FPDF):
    def header(self):
        # Logo
        # self.image('logo.png', 10, 8, 33)
        # Arial bold 15
        self.set_font('Arial', 'B', 15)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'AntiBanana Project Report', 0, 0, 'C')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def chapter_title(self, num, label):
        # Arial 12
        self.set_font('Arial', 'B', 12)
        # Background color
        self.set_fill_color(200, 220, 255)
        # Title
        self.cell(0, 6, 'Chapter %d : %s' % (num, label), 0, 1, 'L', 1)
        # Line break
        self.ln(4)

    def chapter_body(self, body):
        # Times 12
        self.set_font('Times', '', 12)
        # Output justified text
        self.multi_cell(0, 5, body)
        # Line break
        self.ln()

    def print_chapter(self, num, title, body):
        self.add_page()
        self.chapter_title(num, title)
        self.chapter_body(body)

pdf = PDF()
pdf.alias_nb_pages()
pdf.add_page()

# Title Page Content
pdf.set_font('Arial', 'B', 24)
pdf.cell(0, 60, 'AntiBanana', 0, 1, 'C')
pdf.set_font('Arial', '', 16)
pdf.cell(0, 10, 'Deepfake Detection & Protection System', 0, 1, 'C')
pdf.cell(0, 10, 'Full Project Report', 0, 1, 'C')
pdf.cell(0, 10, str(datetime.date.today()), 0, 1, 'C')
pdf.ln(20)

# Executive Summary
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'Executive Summary', 0, 1, 'L')
pdf.set_font('Times', '', 12)
pdf.multi_cell(0, 5, """AntiBanana is a cutting-edge deepfake detection and protection system designed to counter the growing threat of AI-generated media. It combines advanced detection algorithms with a novel protection framework known as MMHI (Multi-Modal Hallucination Injection). The system is built with a modern Next.js frontend and a robust Python/Flask backend, leveraging state-of-the-art machine learning models to identify and neutralize deepfake threats.""")
pdf.ln()

# Chapter 1: System Architecture
body_1 = """The AntiBanana system follows a modern client-server architecture:

1. Frontend (Next.js):
   - A responsive, high-performance web interface built with React and TypeScript.
   - Features real-time analysis dashboards, drag-and-drop file uploads, and interactive visualizations.
   - Integrates specialized components for displaying detection results, including heatmaps and confidence scores.

2. Backend (Python/Flask):
   - A scalable API server handling image processing and model inference.
   - Integrates PyTorch for deep learning operations.
   - Modular design allows for easy addition of new detection methods and protection phases.
"""
pdf.print_chapter(1, 'System Architecture', body_1)

# Chapter 2: Deepfake Detection Capabilities
body_2 = """AntiBanana employs a multi-layered approach to detection:

1. Ensemble Detection Model:
   - Utilizes a RexNet-150 architecture trained on 64x64 image patches for high efficiency and accuracy.
   - Capable of detecting subtle artifacts introduced by GANs and Diffusion models.

2. SynthID Detection:
   - Specialized module to detect Google's invisible SynthID watermarks.
   - Analyzes the frequency domain to identify imperceptible signatures in AI-generated content.
   - Provides confidence metrics and watermark strength indicators.

3. Explainable AI (XAI):
   - Integrates GradCAM++, LIME, RISE, SHAP, and SOBOL methods.
   - Generates heatmaps to visually explain WHICH parts of an image triggered the detection.
   - Helps build user trust by providing transparency into the model's decision-making.

4. C2PA Provenance Verification:
   - Checks for Content Credentials (C2PA) standards.
   - Verifies the digital history and origin of media files.
"""
pdf.print_chapter(2, 'Deepfake Detection Capabilities', body_2)

# Chapter 3: Deepfake Protection (MMHI)
body_3 = """The core innovation of AntiBanana is the Multi-Modal Hallucination Injection (MMHI) framework. This proactive defense mechanism "poisons" images to prevent them from being used to train deepfakes or to disrupt deepfake generation.

Key Features:
- 15-Phase Protection Pipeline: A comprehensive sequence of image transformations including Semantic Decoupling, Frequency Disruption, and Adversarial Noise.
- NanoBanana Breaker: A specialized module targeting transformer-based generators. It uses techniques like Feature Basin Trap Poisoning to cause catastrophic failure in generation models.
- Safety Trigger Injection: Embeds invisible text triggers to activate safety filters in AI models, preventing them from processing the protected image.
"""
pdf.print_chapter(3, 'Deepfake Protection (MMHI)', body_3)

# Chapter 4: Recent Technical Improvements
body_4 = """Recent development sprints have focused on stability and accuracy:

1. Model Architecture Fixes:
   - Resolved mismatches between training (RexNet-150) and inference architectures.
   - Implemented automatic architecture detection from checkpoint keys.

2. Preprocessing Alignment:
   - Standardized image input size to 64x64 to match training data, significantly improving detection accuracy.
   - Updated normalization pipelines for consistency.

3. Enhanced Visualization:
   - Fixed XAI heatmap rendering to correctly overlay saliency maps on original images.
   - Added dedicated UI components for SynthID detection results.
"""
pdf.print_chapter(4, 'Recent Technical Improvements', body_4)

# Conclusion
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'Conclusion', 0, 1, 'L')
pdf.set_font('Times', '', 12)
pdf.multi_cell(0, 5, """AntiBanana represents a significant step forward in media integrity. By combining robust detection with aggressive protection mechanisms, it offers a dual-layer defense against the proliferation of deepfakes. The system is now fully operational with verified detection pipelines and a stable protection framework.""")

pdf.output('AntiBanana_Project_Report.pdf', 'F')
print("PDF generated successfully: AntiBanana_Project_Report.pdf")
