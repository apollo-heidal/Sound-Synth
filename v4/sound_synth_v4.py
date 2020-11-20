'''
Version 4 of sound synthesizer

The naming scheme will stay the same for clarity,
but a more accurate name would be "short random song generator".'''

import numpy as np
import wave, random, os, time

class Synth:
    def __init__(self, filename='test.wav'):
        self.wav = wave.open(filename, 'wb')
        self.fps = 44100
        self.wav.setparams( (2, 2, self.fps, 0, 'NONE', None) ) # (nchannels, sample_width, framerate, nframe, ...)
        self.voices = {}
        self.fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
                        #1597, 2584, 4181, 6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811]
        self.instruments = {    
            1: [1.0, 1.4, 10.0, [0.0, 0.01, 1/3., 2/3., 1.0], [0.0, 1.0, 0.5, 0.0, 0.0]], 
            2: [2**(4/12), 1/5, 1.5, [0.0, 0.2, 0.95, 1.0], [0.0, 1.0, 1.0, 0.0]], 
            3: [2**(7.25/12), 2.0/3.0, 2, [0.0, 0.2, 0.95, 1.0], [0.0, 1.0, 1.0, 0.0]],
            4: [1/2, 1, 5, [0.0, 0.143, 0.333, 0.833, 1.0], [0.0, 1.0, 0.75, 0.6, 0.0]],
        }   #: [c = f*x, m = c*x, pd, tlist, alist]


    def rescale(self, data):
        '''Takes numpy array and normalizes it to (2*16 - 1) * 0.7
        This utilizes only %70 of 2-byte range, but is still loud enough to be heard in audio program '''
        _max = np.amax(data)
        _min = np.amin(data)
        return data * (2**16 - 1) / (_max - _min) * 0.7


    def envelope(self, data, tlist=None, alist=None, _is_random=True):
        '''takes iterable data and generates a list of "control points"
        
        list ctrl_points = [[time_0, amp_0], [time_1, amp_1],..., [time_n, amp_n]]
        
        The values of the samples in between these control points
        is interpolated by creating an array of amp scale factors.

        The amp values range from amp_n-1 to amp_n, and can be linearly
        or geometrically spaced.

        The data array, from time_n-1:time_n, is then multiplied 
        by the array of scale factors.'''
        if _is_random:
            ctrl_points = [[0, 0.00000001], [1, 0.00000001]]    # zer0 cannot be used as an endpoint for np.geomspace

            for _ in range(random.randint(1,7)):
                ctrl_points.append([random.random(), random.random()])
            ctrl_points.sort()

            for i, p in enumerate(ctrl_points):
                if i == 0:  # skip 0 to avoid slicing error
                    continue
                t0 = int(ctrl_points[i-1][0] * data.shape[0])
                t1 = int(p[0] * data.shape[0])
                a0 = ctrl_points[i-1][1] * data.shape[0]
                a1 = p[1] * data.shape[0]
                data[t0:t1] *= np.geomspace(a0, a1, num=t1-t0)
            return data
        else:
            for i, t in enumerate(tlist):
                if i == 0 :
                    continue
                t0 = int(tlist[i-1] * data.shape[0])
                t1 = int(t * data.shape[0])
                a0 = alist[i-1] * data.shape[0]
                a1 = alist[i] * data.shape[0]
                data[t0:t1] *= np.linspace(a0, a1, num=t1-t0)
            return data


    def rhythm(self):
        '''Can be called to repeat an element on one of the channels

        -- repetitions is the number of times per section (A1, B, A2) that the element repeats
        -- on_ratio is the decimal value of time_on / total_time; comparable to a duty cycle'''
        for part in range(3):
            if part != 1:
                self.voices = {}
                nvoices = random.randint(7,len(self.fibonacci))
                for n in range(nvoices):
                    self.voices[n] = np.zeros( (self.fps * 60) )

                for voice, data in self.voices.items():
                    if part != 1:
                        repetitions = self.fibonacci[voice]
                        measure = int(data.shape[0] / repetitions)
                        tone = self.geometric_fm_generator(measure)
                        
                        for rep in range(repetitions):
                            start = rep * measure
                            stop = (rep + 1) * measure
                            data[start:stop] += tone
                        
                        data = self.envelope(data)
                self.write_data(part=part)
                
            else:
                data = self.geometric_fm_generator( (self.fps * 120), _use_instruments=True)
                data = self.rescale(data)
                self.write_data(data_in=data, part=part)

            print(part)
            
    
    def geometric_fm_generator(self, nsamples, _use_instruments=False) :
        if _use_instruments == False:
            carrier_0 = (random.random() * self.fps / 5)
            carrier_1 = (random.random() * self.fps / 5)
            mod_0 = random.randint(1, self.fps / 10)
            mod_1 = random.randint(1, self.fps / 10)
            peak_deviation = random.randint(1, 100)

            modulator = np.sin( np.geomspace(mod_0, mod_1, num=nsamples) ) * peak_deviation
            data = np.sin( np.geomspace(carrier_0, carrier_1, num=nsamples) + modulator )
            return data
        else:
            data = np.zeros((nsamples))
            my_str = 'Hello, World! You are about to enter the Matrix...'
            section = int(nsamples / len(my_str))

            for i, char in enumerate(my_str):
                if i == 0:
                    continue
                
                instrument = self.instruments[random.randint(1,4)]
                fx = ord(char) * 20
                cx = instrument[0] * fx 
                mod = instrument[1] * cx
                pd = instrument[2]
                
                start = (i -1) * section
                stop = i * section
                modulator = np.sin( np.linspace(0, mod, num=section) ) * pd
                data[start:stop] += self.envelope(np.sin( np.linspace(0, cx, num=section) + modulator ), instrument[3], instrument[4], _is_random=False)
            return data


    def write_data(self, data_in=None, part=-1):
        '''stacks channel arrays and resets channel attributes
        writes data to open wave file
        '''
 
        if part != 1:
            # combine voices
            channel1 = np.zeros( (self.fps * 60, ) )
            channel2 = np.zeros( (self.fps * 60, ) )
            for voice, data in self.voices.items():
                if voice % 2 == 0:
                    channel1 += data
                else:
                    channel2 += data
            del self.voices
            # stack channels and write to file
            final_data = np.stack(( self.rescale(channel1), self.rescale(channel2) ), axis=1)
            self.wav.writeframes( np.short(final_data) )
        else:
            final_data = np.reshape(data_in, (-1, 2))
            self.wav.writeframes( np.short(final_data))

        
if __name__ == "__main__":
    t0 = time.time()
    print(t0)

    song = Synth()
    song.rhythm()
    song.wav.close()

    print('\n%.2f' % ((time.time() - t0) * 1000), 'ms')
    print('output directory:', os.getcwd(), '\n')