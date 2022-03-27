class Break:
    def __init__(self):
        self.proj_name = []
        self.proj_dur = []
        self.proj_app = []
        self.proj_score = []
        self.end_time = []

    def addBreak(self, proj_name, proj_dur, proj_app, proj_score, end_time):
        self.proj_name.append(proj_name)
        self.proj_dur.append(proj_dur)
        self.proj_app.append(proj_app)
        self.proj_score.append(proj_score)
        self.end_time.append(end_time)

    def extendBreak(self, proj_dur, end_time):
        self.proj_dur[-1] += proj_dur
        self.end_time[-1] = end_time

    def setEffect(self, score):
        self.break_eff = score
