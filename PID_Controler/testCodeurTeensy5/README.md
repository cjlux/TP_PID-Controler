# TP_PID-Controler

The `testCodeurTeensy5.ino` file is processed by the __ProcessInoFile__ method of the __Monitor__ class to find out:

- lines that contain the keyword `case`, like `case '5': // Kd*1.25`<br>
These lines give information to create push puttons in the GUI.<br>
They are formatted following the template:    `case 'string1': // comment`<br>
where:
    - `string1`: is the label of the push button,
    - `comment`: gives a comment displayed near the push button.
    
- lines that contain the keyword `mess +=`, like `mess += ",KP,";   // Kp gain`<br>
These lines give information to create fields in the GUI  that display the content of important variables of the .ino program<br>
They are formatted following the template: `mess +=  ",string,": // comment`, where:
    - `string1`: is the label of the display field
    - `comment`: gives a comment displayed in a pop-up window when the mouse cursor is in a display fieled.
