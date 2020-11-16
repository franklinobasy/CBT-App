class Question():
    def __init__(self, file_question, file_option):
        self.file_question = file_question
        self.file_option = file_option

        with open (file_question, 'r') as obj:
            self.raw = obj.read()


        with open(self.file_option, 'r') as obj:
            self.raw_opt = obj.read()

        self.unworked_question = self.makeQuestion()
        self.unworked_option = self.makeOption()

    def makeQuestion(self):
        self.question = self.raw.split('#')
        return self.question

    def sortQuestion(self):
        self.sorted_questions = []
        for item in self.unworked_question:
            number_and_question = item.split('*')
            number_and_question = tuple(number_and_question)
            self.sorted_questions.append(number_and_question)
        self.sorted_questions.insert(0,"")
        return self.sorted_questions

    def makeOption(self):
        self.options = self.raw_opt.split('#')
        return self.options

    def sortOption(self):
        self.sorted_option = []
        for item in self.unworked_option:
            options_ = item.split(',')
            options_ = tuple(options_)
            self.sorted_option.append(options_)
        self.sorted_option.insert(0, '')
        return self.sorted_option
    
if __name__ == '__main__':
    j = Question('questions.txt','options.txt')
    print(j.sortQuestion())
