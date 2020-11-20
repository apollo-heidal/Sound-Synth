import os
import numpy as np
from appJar import gui


def writeWave(data):
    import wave
    w = wave.open(app.getEntry('file_out') + '.wav', "w")
    w.setnchannels(1)
    w.setframerate(int(app.getEntry('sampling_rate'))) 
    w.setsampwidth(2)  # N bytes per sample
    w.setnframes(data.shape[0])
    w.writeframes(np.short(data))
    w.close()
    app.infoBox('Success!', 'Sound data has been written to ' + app.getEntry('file_out') + '.wav')
 

def envelope(data):
    total_samples = data.shape[0]
    control_points.append([0.0, 0.0])
    
    for i in range(len(control_points)-1):
        t_0 = int(control_points[i][0] / 100 * total_samples)
        t_1 = int(control_points[i + 1][0] / 100 * total_samples)

        a_0 = control_points[i][1] / 100.0
        a_1 = control_points[i+1][1] / 100.0

        # special case for last section of envelope
        if i == (len(control_points)-2):
            amp_mod = np.linspace(a_0, a_1, num=(total_samples - t_0))
            data[t_0:total_samples] *= amp_mod
            break

        amp_mod = np.linspace(a_0, a_1, num=(t_1 - t_0))
        #amp_mod = amp_mod**np.e
        data[t_0:t_1] *= amp_mod   
    return data


def makeSine():
    frequency       = app.getEntry('frequency')
    sampling_rate   = app.getEntry('sampling_rate')
    duration        = app.getEntry('duration')
    if frequency and sampling_rate and duration:
        total_radians = 2*np.pi * float(frequency)
        total_samples = int(int(sampling_rate) * float(duration))
        amplifier = 32767 #max 16-bit number

        sine_tone = np.sin(np.linspace(0, total_radians, num=total_samples))
        wav_data = envelope(sine_tone * amplifier)
        writeWave(wav_data)
    else:
        app.errorBox('Field Error!', 'Please populate settings before clicking \'Generate\'.')


def primaryButtons(name):
    if name == 'Exit':
        app.stop()
    if name == 'Generate':
        wave_type = app.getRadioButton('wave_type')
        if wave_type == 'Sine':
            makeSine()
        elif wave_type == 'Square':
            print('Square needs to be finished')  
        elif wave_type == 'Triangle':
            print('Triangle needs to be finished') 


def controlPointsList():
    if app.getEntry('time_point') and app.getEntry('amp_value'):
        t_point = float(app.getEntry('time_point').strip())
        a_value = float(app.getEntry('amp_value').strip())
        control_points.append([t_point, a_value])
        
        app.clearEntry('time_point')
        app.clearEntry('amp_value')
        app.setLabel('control_points', control_points)
        app.setFocus('time_point')
    else:
        app.errorBox('Field Error!', 'Please fill both fields before clicking \'Add to list\'.')


if __name__ == "__main__":
    control_points = [[0.0, 0.0]]
    
    with gui('Synth', sticky='nwse') as app:
        # GUI settings
        app.setBg('#266726')
        app.setFg('#000000')
        app.setFont(14)
        app.setStretch('both')

        with app.labelFrame('settings', row=0, column=0, sticky='nwse', label='Settings'):
            app.addLabelEntry('frequency', label='Frequency:\t')
            app.addLabelEntry('sampling_rate', label='Sampling rate:\t')
            app.addLabelEntry('duration', label='Note duration:\t')
            app.addLabelEntry('file_out', label='Output file:\t')

            with app.labelFrame('Type of sound wave', sticky='w'):
                app.addRadioButton('wave_type', 'Sine')
                app.addRadioButton('wave_type', 'Square')
                app.addRadioButton('wave_type', 'Triangle')

        with app.labelFrame('envelope', row=0, column=1, sticky='nwse', label='Envelope Control Points'):
            
            with app.labelFrame('time', label='Time'):
                app.addLabelEntry('time_point', label='')
            
            with app.labelFrame('amp', row=0, column=1, label='Amplitude'):
                app.addLabelEntry('amp_value', label='')

            with app.labelFrame('control_points', row=1, colspan=2, label='Control points'):
                app.addLabel('control_points', control_points)

            app.addButton('Add to list', controlPointsList, colspan=2)
            app.setStre

        with app.labelFrame('buttons', hideTitle=True, sticky='', colspan=2):
            app.addButtons(['Generate', 'Reset', 'Exit'], primaryButtons)

        