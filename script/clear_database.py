from database import db

def main(**kwargs):
    count = db.project.count()
    db.project.drop()
    print 'Droped %d projects' % count
