from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ====================================================================================
#                         DATABASE MODELS/TABLES
# ====================================================================================

# user table
class User(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      username = db.Column(db.String(150), unique=True, nullable=False)
      student_id = db.Column(db.String(150), unique=True, nullable=False)
      password = db.Column(db.String(150), nullable=False)  # Stores hashed password

      def __repr__(self):
         return f'<User {self.username}>'

# # activity table 
# class Activity(db.Model):
#       id = db.Column(db.Integer, primary_key=True)
#       title = db.Column(db.String(200), nullable=False)
#       user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

#       def __repr__(self):
#          return f'<Activity {self.title} on {self.date}>'