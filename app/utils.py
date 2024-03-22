from flask import Blueprint, request, flash, render_template, redirect, url_for, g
from db import mysql

utils = Blueprint('utils', __name__, template_folder= 'app/templates')
@utils.route('/')
@utils.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

