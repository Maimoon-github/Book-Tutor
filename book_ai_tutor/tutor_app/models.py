from django.db import models

class Book(models.Model):
    pdf = models.FileField(upload_to='pdfs/')
    content = models.TextField(blank=True)

    def __str__(self):
        return self.pdf.name

class Chapter(models.Model):
    book = models.ForeignKey(Book, related_name='chapters', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)

    class Meta:
        unique_together = ('book', 'number')
        ordering = ['number']

    def __str__(self):
        return f"Chapter {self.number}: {self.title}"

class Lesson(models.Model):
    chapter = models.ForeignKey(Chapter, related_name='lessons', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('chapter', 'number')
        ordering = ['number']

    def __str__(self):
        return f"Lesson {self.number}: {self.title}"

class Question(models.Model):
    lesson = models.ForeignKey(Lesson, related_name='questions', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    text = models.TextField()
    answer = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('lesson', 'number')
        ordering = ['number']

    def __str__(self):
        return f"Q{self.number}: {self.text[:50]}..."
