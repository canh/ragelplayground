#!/usr/bin/env python3

import subprocess
from os.path import join
from tempfile import TemporaryDirectory
from flask import Flask, request
from markupsafe import escape

html = """<!DOCTYPE html>
<html>
    <head>
        <style>
            .layout {
              height: calc(100vh - 20px);

              display: grid;
              grid:
                "left right" 1fr
                "o1 o2" auto
                "o3 o4" auto
                / 1fr 1fr;
              gap: 8px;
            }

            .left { grid-area: left; }
            .right { grid-area: right; }
            .bottom { grid-area: bottom; }
            .o1 { grid-area: o1; }
            .o2 { grid-area: o2; }
            .o3 { grid-area: o3; }
            .o4 { grid-area: o4; }

            textarea {
              font-family: monospace;
            }
        </style>
    </head>
    <body> 
    <form class="layout" hx-post="/" hx-trigger="change,keyup delay:500" hx-target=".right">
        <textarea name="input" class="left"></textarea>
        <label class="o1">
            <input type="checkbox" name="args" value="-d">
            Do not remove duplicates from action lists
        </label>
        <label class="o2">
            Host language
            <select name="args">
            <option value="-C">C, C++, Obj-C or Obj-C++</option>
                <option value="-D">D</option>
                <option value="-Z">Go</option>
                <option value="-Z">Go</option>
                <option value="-J">Java</option>
                <option value="-R">Ruby</option>
                <option value="-A">C#</option>
                <option value="-O">OCaml</option>
            </select>
        </label>
        <label class="o3">
            <input type="checkbox" name="args" value="-L">
            Inhibit writing of #line directives
        </label>
        <label class="o4">
            Code style
            <select name="args">
                <optgroup label="C/D/Java/Ruby/C#/OCaml">
                    <option value="-T0">Table driven FSM</option>
                </optgroup>
                <optgroup label="C/D/Ruby/C#/OCaml">
                    <option value="-T1">Faster table driven FSM</option>
                    <option value="-F0">Flat table-driven FSM</option>
                    <option value="-F1">Faster flat table-driven FSM</option>
                </optgroup>
                <optgroup label="C/D/C#/OCaml">
                    <option value="-G0">Goto-driven FSM</option>
                    <option value="-G1">Faster goto-driven FSM</option>
                </optgroup>
                <optgroup label="C/D">
                    <option value="-G2">Really fast goto-driven FSM</option>
                </optgroup>
            </select>
        </label>
        <textarea class="right"></textarea>
    </form>
    <script src="https://unpkg.com/htmx.org@1.9.12" integrity="sha384-ujb1lZYygJmzgSwoxRggbCHcjc0rB2XoQrxeTUQyRjrOnlCoYta87iKBWq3EsdM2" crossorigin="anonymous"></script>
    <script>
    htmx.logAll();
    document.querySelector('textarea[name=input]').addEventListener('keydown', function(e) {
        if (e.key == 'Tab') {
          e.preventDefault();
          var start = this.selectionStart;
          var end = this.selectionEnd;

          // set textarea value to: text before caret + tab + text after caret
          this.value = this.value.substring(0, start) + '\\t' + this.value.substring(end);

         // put caret at right position again
        this.selectionStart = this.selectionEnd = start + 1;
      }
    });
    </script>
    </body>
</html>
"""

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def handle():
    if request.method == "GET":
        return html
    else:
        with TemporaryDirectory() as tmp:
            with open(join(tmp, "input.txt"), "wt") as fp:
                print(request.form.get("input"), file=fp, end=None)
            args = request.form.getlist("args")
            cmd = ["ragel", *args, join(tmp, "input.txt"), "-o", join(tmp, "output.txt")]
            try:
                child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                stdout, _ = child.communicate()
            except Exception as e:
                return escape("Can't run ragel: " + e.message)
            if child.returncode == 0:
                with open(join(tmp, "output.txt"), "rt") as fp:
                    return escape(fp.read())
            else:
                return escape(stdout)

if __name__ == "__main__":
    app.run(debug=True)
