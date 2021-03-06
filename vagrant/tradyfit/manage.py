#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
  import coverage
  COV = coverage.coverage(branch=True, include='app/*')
  COV.start()

from app import create_app, db
from app.models import Category, Item, User, Message
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
  return dict(app=app, db=db, Category=Category, Item=Item, User=User,
              Message=Message)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test(coverage=False):
  """Run the unit/integration tests. With coverage also functional tests"""

  path = os.path.dirname(os.path.abspath(__file__))

  if coverage and not os.environ.get('FLASK_COVERAGE'):
    import sys
    os.environ['FLASK_COVERAGE'] = '1'
    os.execvp(sys.executable, [sys.executable] + sys.argv)

  import unittest
  tests_dir = os.path.join(path,"tests")
  tests = unittest.TestLoader().discover(tests_dir)
  unittest.TextTestRunner(verbosity=2).run(tests)

  if COV:
    COV.stop()
    COV.save()
    print('Coverage Summary:')
    COV.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'tmp/coverage')
    COV.html_report(directory=covdir)
    print('HTML version: file://%s/index.html' % covdir)
    COV.erase()

@manager.command
def acceptance_test():
  """Run the functional tests."""
  import unittest
  path = os.path.dirname(os.path.abspath(__file__))
  tests_dir = os.path.join(path,"tests/functional")
  tests = unittest.TestLoader().discover(tests_dir)
  unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def deploy():
  """Run deployment tasks."""
  from flask.ext.migrate import upgrade

  # migrate database to latest revision
  upgrade()
  # create categories
  Category.insert_categories()


if __name__ == '__main__':
  manager.run()