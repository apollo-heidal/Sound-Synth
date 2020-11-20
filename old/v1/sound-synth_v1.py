import numpy as np
import matplotlib.pyplot as plt
import os, json, time

def configure():
    print('\nWelcome to my note synthesizer!\
        \nThis version will ask for a frequency and provide steps \
        \nto modify that sound. When prompted for paired values,\
        \nadd a space after the first and press enter after the second.\
        \nPress q then enter at any time to move to the next step.\
        \nEnjoy, Po\n')
    

    with open('config_v1.json') as json_config:
        use_json = input('Config file found. Use file (Y) or create new (n)? ')
        if use_json != 'n':
            config = json.load(json_config)
            return config    

    config = {}

    config['frequency'] = float(input('\nEnter note frequency: '))
    
    config['duration'] = float(input('Enter note duration in seconds: '))

    config['sampling_rate'] = int(input('Enter a sampling rate: '))

    config['filename'] = input('Enter name of output file (include .wav): ')

    # overtones
    add_overtones = input('Add overtones (Y/n)? ').strip().lower()
    if add_overtones != 'n' and add_overtones != 'q':        
        config['overtones'] = [[config['frequency'], 1.0]]
        
        creation_method = input('\nGenerate procedurally (G) or manually (m)? ').strip().lower()
        if creation_method == 'm':
            print('Manual generation selected.\n\
                \nEnter an overtone frequency (f > fundamental)\
                \nand the amplitude of the overtone (0.0 < a < 1.0).')

            user_input = input('\nEnter overtone 1: ').split()
            while user_input[0] != 'q':
                config['overtones'].append( [float(user_input[0]), float(user_input[1])] )
                print('Current overtones:', config['overtones'])
                user_input = input('\nEnter overtone %d: ' % len(config['overtones'])).split()

        else:
            print('Procedural generation selected.\n')
            num_overtones = int(input('Enter number of overtones: '))
            random_gen = input('Use random values (Y/n)? ').strip()
            if random_gen == 'n':
                mul_factor = float(input('Enter frequency multiplier (fm > 1.0): '))
                amp_factor = float(input('Enter amplitude decay factor (0.0 < d < 1.0): '))
                for i in range(num_overtones):
                    fx = config['overtones'][i][0] * mul_factor
                    amp = config['overtones'][i][1] * amp_factor
                    config['overtones'].append([fx, amp])
            else:
                for i in range(num_overtones):
                    random_fx = (np.random.random() + 1) * (config['sampling_rate'] / 4)
                    random_amp = np.random.random()
                    config['overtones'].append([random_fx, random_amp])

    # envelope
    print('\nEnvelope control pairs are used to modulate amplitude\
        \nduring a note. Both values should be between, and may\
        \ninclude, 0.0 and 100.0 percent. The first value is a point\
        \nalong the time axis and the second is the percent of maximum\
        \namplitude at that point. The amplitude of the note is \
        \nlinearly interpolated between these points. Quitting defaults\
        \nto constant 100% note amplitude.')
    config['amp_ctrl_points'] = []
    while True:
        user_input = input('\nEnter control pair #%d: ' % (len(config['amp_ctrl_points']) + 1)).split()
        if user_input[0] == 'q':
            break
        t = float(user_input[0])
        amp = float( user_input[1])
        config['amp_ctrl_points'].append([t, amp])
        print('Current control pairs: ', sorted(config['amp_ctrl_points']))
    config['amp_ctrl_points'] = sorted(config['amp_ctrl_points'])

    with open('config_v1.json', 'w') as json_config:
        json.dump(config, json_config)
        
    return config


def makeSine(config):
    fx, samples = config['frequency'], config['sampling_rate'] * config['duration']
    return np.sin(np.linspace(0, (2*np.pi * fx), num=samples))


def addOvertones(data, config):
    '''adds overtones to a note using additive synthesis'''
    if not config['overtones']:
        return data

    for overtone in config['overtones']:
        rad =  2*np.pi * overtone[0]
        amp = overtone[1]
        t_s = data.shape[0]
        data += np.sin(np.linspace(0, rad, num=t_s)) * amp
    return data


def envelope(data, config):
    if not config['amp_ctrl_points']:
        return data

    t_s = data.shape[0]
    ctrl_points = config['amp_ctrl_points']
    ctrl_points.append([100.0, 0])

    for i in range(len(ctrl_points)-1):
        t_0 = int(ctrl_points[i][0] * t_s / 100)
        t_1 = int(ctrl_points[i + 1][0] * t_s/ 100)

        a_0 = ctrl_points[i][1] / 100
        a_1 = ctrl_points[i+1][1] / 100

        amp_mod = np.linspace(a_0, a_1, num=(t_1-t_0))
        #amp_mod = amp_mod**np.e
        data[t_0:t_1] *= amp_mod   
    return data


def amplify(data):
    data_max = np.amax(data)
    data_min = np.amin(data)
    return data * ( (2**16 - 1) / (data_max - data_min) * 0.9)


def writeWave(data, config):
    import wave
    w = wave.open('wav_files/' + config['filename'], "w")
    w.setnchannels(1)
    w.setframerate(config['sampling_rate']) 
    w.setsampwidth(2)  # N bytes per sample
    w.setnframes(data.shape[0])
    w.writeframes(np.short(data))
    w.close()
    print('\nOutput file: ' + os.getcwd() + '\\' + config['filename'] + '\n')


if __name__ == "__main__":
    config = configure()
    
    t_0 = time.time()
    # main pipeline
    data       = makeSine(config)
    data       = addOvertones(data, config)
    data       = envelope(data, config)
    data       = amplify(data)

    # write data to wave file
    writeWave(data, config)
    
    # calculates and prints time elapsed during the generate stage
    t_update = time.time()
    print('Program run time (excluding configuration): %.2f ms\n' % (1000 * (t_update - t_0)) )