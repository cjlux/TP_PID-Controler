# Processing the file  `testCodeurTeensy5.ino`

The `testCodeurTeensy5.ino` file is processed by the __ProcessInoFile__ method of the __Monitor__ class to find out:

- The lines that contain the keyword `case`, like `case '5': // Kd*1.25`. These lines give information to create push puttons in the GUI. They are formatted following the template: <br>   `case 'string1': // comment`, where:<br>
    - `string1`: is the label of the push button to create,
    - `comment`: gives a comment displayed near the push button.
    
- The lines that contain the keyword `mess +=`, like `mess += ",KP,";   // Kp gain`<br>
These lines give information to create fields in the GUI  that display the content of important variables of the .ino program. 
They are formatted following the template:<br>
`mess +=  ",string,": // comment`, where:
    - `string`: is the label of the display field,
    - `comment`: gives a comment displayed in a pop-up window when the mouse cursor is in a display fieled.
