'''
10/22 - I spent lab time converting the code in Arun's square and triagle python files
        to fit my own files format. The main difference is that I populate arrays using
        np.linspace instead of using for-loops to populate lists.
        
        I have not yet figure out the sawtooth or triangle waves. The sound is qualitatively
        similar, but upon further inspection the waveforms are dissimilar.
'''
import numpy as np

def get_user_scale():
    scale_type = input('What kind of scale do you want to hear (chromatic, major, minor)? ').lower().strip()
    starting_frequency = float(input('What is the starting frequency of your scale? ').strip())
    return scale_type, starting_frequency


def make_scale_array(scale_type, starting_frequency):
    '''This function...
    '''
    scale_dict = {  'chromatic':    {'notes_in_scale': 13, 'cents_per_interval': [0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]},
                    'major':        {'notes_in_scale': 8, 'cents_per_interval': [0, 200, 200, 100, 200, 200, 200, 100]},
                    'minor':        {'notes_in_scale': 8, 'cents_per_interval': [0, 200, 100, 200, 200, 100, 200, 200]}}
    
    notes_in_scale = scale_dict[scale_type]['notes_in_scale']
    tone_intervals = scale_dict[scale_type]['cents_per_interval']

    scale_array = np.empty((notes_in_scale, 1))
    cents_from_base = 0
    for i in range(len(scale_array)):
        cents_from_base += tone_intervals[i]
        scale_array[i][0] = starting_frequency * 2**(cents_from_base/1200.0)
    
    return scale_array


def write_wave(data, sampling_rate, file_name='out.wav'):
    import wave
    w = wave.open('wav_files/' + file_name, "w")
    w.setnchannels(1)
    w.setframerate(sampling_rate) 
    w.setsampwidth(2)  # N bytes per sample
    w.setnframes(data.shape[0])
    w.writeframes(np.short(data))
    w.close()
    print('\nOutput file:\t' + file_name + '\nOpen in audio program to hear/view your creation!')
    
    
def envelope(tone_data):
    total_samples = tone_data.shape[0]
    da_dt = []

    print('Please type a time point, press \'Enter\', then type it\'s corresponding amplitude.\
        \nPlease be sure that these percentages are between 0.0 and 100.0.\
        \nPress \'q\' then \'Enter\' when you are done adding points.')

    while True:
        time_point = input('\nEnter time point #%d: ' % (len(da_dt) + 1) )
        if time_point == 'q':
            break
        amp_value = float( input('And it\'s amplitude: ') ) / 100
        time_point = float(time_point) / 100
        da_dt.append([time_point, amp_value])

    da_dt = sorted(da_dt)
    da_dt.insert(0, [0, 0])
    da_dt.append([1.0, 0])
    print(da_dt)

    for i in range(len(da_dt)-1):
        start = int(da_dt[i][0] * total_samples)
        stop = int(da_dt[i + 1][0] * total_samples)

        # special case for last section envelope
        if i == (len(da_dt)-2):
            amp_mod = np.linspace(da_dt[i][1], da_dt[i + 1][1], num=(total_samples - start))
            tone_data[start:total_samples] *= amp_mod
            break

        amp_mod = np.linspace(da_dt[i][1], da_dt[i + 1][1], num=(stop - start))
        #amp_mod = amp_mod**np.e
        tone_data[start:stop] *= amp_mod   

    return tone_data


def make_sine(scale_array, sampling_rate, amp, nyquist):
    duration = 5
    fundamental = 880
    total_radians = 2 * np.pi * fundamental
    t_axis = np.linspace(0, total_radians, num=(sampling_rate * duration))
    sine_tone = np.sin(t_axis) * amp
    env_tone = envelope(sine_tone)
    write_wave(env_tone, sampling_rate, file_name='sine_adsr.wav')


def make_sawtooth():
    pass


def make_triangle(scale_array, sampling_rate, amp, nyquist):
    tones = np.zeros((scale_array.shape[0], sampling_rate))
    for i in range(len(scale_array)):
        fundamental = scale_array[i][0]
        frequency = fundamental
        n = 1
        while frequency < nyquist:
            frequency = fundamental * n
            total_radians = 2 * np.pi * frequency
            x = np.linspace(0, total_radians, num=sampling_rate)
            tones[i] += np.cos(x)
            n += 2
        '''
        a_max = tones[i].max()
        a_min = tones[i].min()
        displacement = a_max - a_min
        print(displacement)
        tones *= amp / displacement
        '''
    write_wave(tones * amp, sampling_rate, file_name='triangle.wav')


def make_square(scale_array, sampling_rate, amp, nyquist):
    ''' make_square takes in an array of frequencies in scale and sampling rate 
        returns array of samples with square wave form'''

    tones = np.zeros((scale_array.shape[0], sampling_rate))
    for i in range(len(scale_array)):
        fundamental = scale_array[i][0]
        frequency = fundamental
        n = 1
        while frequency < nyquist:
            frequency = fundamental * n
            total_radians = 2 * np.pi * frequency
            x = np.linspace(0, total_radians, num=sampling_rate)            
            A = amp / n
            tones[i] += (A * np.sin(x))
            n += 2
    write_wave(tones, sampling_rate, file_name='square.wav')


def remove_clipping(tone_data):
    for tone in tone_data:
        i = 1
        while True:
            if abs(tone[-i]) > 1500:
                tone[-i] = 0.0
                i += 1
            else:
                break
    return tone_data 


def press():
    global fundamental_frequency
    fundamental_frequency = win.getEntry('Please enter a frequency:')
    win.setLabel('completion', 'Good job! Your .wav file is being created.\
                                \nHere is %.1f Hz' % float(fundamental_frequency))


if __name__ == "__main__":
    # settings
    sampling_rate = 44100 #Hz
    duration_per_note = 1 
    nyquist = sampling_rate / 2
    amp = 10**(96.0/20.0) / 2
    
    # get scale type and starting tone from user
    #scale_type, starting_frequency = get_user_scale()
    scale_type = 'major'
    starting_frequency = 440

    # create array of frequencies in user's scale
    scale_array = make_scale_array(scale_type, starting_frequency)
    
    # create a square wave scale from scale_array
    #make_square(scale_array, sampling_rate, amp, nyquist)
    #make_triangle(scale_array, sampling_rate, amp, nyquist)
    make_sine(scale_array, sampling_rate, amp, nyquist)