import fitz  # PyMuPDF
from django.core.management.base import BaseCommand
from tutor_app.models import Book, Chapter, Lesson, Question

class Command(BaseCommand):
    help = 'Extracts data from the provided PDF and populates the database.'

    def handle(self, *args, **options):
        pdf_path = 'thiswayEnglishBook-5-2020 - Punjab -20.01.22.pdf'
        doc = fitz.open(pdf_path)
        book_title = 'This Way English Book 5 (Punjab 2020)'
        book, _ = Book.objects.get_or_create(title=book_title)

        chapter = None
        lesson = None
        chapter_num = 0
        lesson_num = 0
        question_num = 0

        for page in doc:
            text = page.get_text()
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Example parsing logic (customize as needed):
                if line.lower().startswith('chapter'):
                    chapter_num += 1
                    lesson_num = 0
                    chapter = Chapter.objects.create(
                        book=book,
                        number=chapter_num,
                        title=line
                    )
                elif line.lower().startswith('lesson'):
                    lesson_num += 1
                    question_num = 0
                    lesson = Lesson.objects.create(
                        chapter=chapter,
                        number=lesson_num,
                        title=line,
                        content=''  # Optionally accumulate content
                    )
                elif line.lower().startswith('q') or line.lower().startswith('question'):
                    question_num += 1
                    Question.objects.create(
                        lesson=lesson,
                        number=question_num,
                        text=line,
                        answer=None
                    )
                else:
                    # Optionally accumulate lesson content
                    if lesson:
                        lesson.content = (lesson.content or '') + line + '\n'
                        lesson.save()
        self.stdout.write(self.style.SUCCESS('PDF extraction and import complete.'))
