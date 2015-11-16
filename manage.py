﻿#!/usr/bin/env python
import os
from app import  create_app,db
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify
from datetime import datetime
from app.models import SVSFaceTab,SVSuserReg,SVSIpCamReg


app = create_app(os.getenv('SVS_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)




def make_shell_context():
    return dict(app=app, db=db,SVSuserReg=SVSuserReg,SVSIpCamReg=SVSIpCamReg,SVSFaceTab=SVSFaceTab)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)




@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()