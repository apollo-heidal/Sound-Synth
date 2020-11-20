import numpy as np
from numpy import pi, sin, e
import time, wave, random, os

class Synth:
    '''Synth class can be used to generate sounds using pseudo-random control variables

    ---_is_random being True triggers randomization branch in generator methods
    ---default dur gets overwritten when _is_random == True

    '''
    def __init__(self, _is_random=False, dur=3, filename='test.wav'):
        self._is_random = _is_random    #boolean that triggers random branches with methods

        self.wav = wave.open(filename, 'wb')
        self.wav.setparams((2, 2, 44100, 0, 'NONE', None)) #(nchannels, sample_width, framerate, nframe, ...)
        self.channel1 = None
        self.channel2 = None
        self.fps = self.wav.getframerate()

        # storing phase is require when envelope does not start/stop at 0 amplitude
        # clicking occurs otherwise
        self.sine_phase = 0
        self.fm_phase = 0
        self.carrier_phase = 0

        self.dur = dur
        self.samples = dur * self.fps
        self.rand_samples = 0           #reset to zero in self.write_data


    def rescale(self, data):
        '''takes any value or container that supports broadcasting
        and scales it to 2-byte range'''
        _max = np.amax(data)
        _min = np.amin(data)
        data *=  (2**16 - 1) / (_max - _min) * 0.7  #np.short() will clip samples so I scale to %70 of 2-byte max


    def random_envelope(self, data):
        '''takes iterable data and generates a list of "control points"
        list ctrl_points = [[time_0, amp_0], [time_1, amp_1],..., [time_n, amp_n]]
        
        
        The values of the samples in between these control points
        is interpolated by creating an array of amp scale factors.

        The amp values range from amp_n-1 to amp_n, and can be linearly
        or geometrically spaced.

        The data array, from time_n-1:time_n, is then multiplied 
        by the array of scale factors.

        '''
        ctrl_points = [[0, 0.00000001], [1, 0.00000001]]

        for _ in range(random.randint(1,21)):
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


    def envelope(self, data):
        if self._is_random == True:
            self.random_envelope(data)
            return
        #ctrl_points = [[0, 0], [1, 0]]
    
    
    def sine_generator(self, fx=440):
        if self._is_random == True:
            if self.rand_samples == 0:
                self.rand_samples = random.random() * 5 * self.fps
            fx = (220 + ( random.random() * self.fps / 7 )) * 2*pi
            n_overtones = 10
            self.channel1 = sin( np.linspace(0, fx/10, num=self.rand_samples)) * n_overtones/2
            for i in range(2,n_overtones):
                self.channel1 += sin( np.linspace(0, fx*i/10, num=self.rand_samples)) * n_overtones/2*i
            self.envelope(self.channel1)
            self.rescale(self.channel1)
        else:
            self.sine_phase += 2*pi*fx / self.samples
            self.channel1 = sin( np.linspace(self.sine_phase, 2*pi*fx, num=self.samples) )
            self.envelope(self.channel1)
            self.sine_phase = (2*pi*fx) % (2*pi)


    def fm_generator(self, carrier_fx=220, mod_fx=55, mod_range=20):
        if self._is_random ==True:
            if self.rand_samples == 0:
                self.rand_samples = random.random() * 5 * self.fps

            carrier_fx = 24 + ( random.random() * self.fps / 7 )
            mod_0 = random.randint(1, self.fps / 5)
            mod_1 = random.randint(1, self.fps / 5)
            mod_amp = random.randint(1, 10)

            modulator = sin( np.geomspace(mod_0, mod_1, num=self.rand_samples) ) * mod_amp
            self.channel2 = sin( np.geomspace(0.000001, 2*pi *carrier_fx, num=self.rand_samples) + modulator)

            self.envelope(self.channel2)
            self.rescale(self.channel2)
        else:
            self.fm_phase += (2*pi * mod_fx) / self.samples
            self.carrier_phase += (2*pi * carrier_fx) / self.samples

            modulator = sin( np.geomspace(2*pi * mod_fx, self.fm_phase, num=self.samples) ) * mod_range
            self.channel2 = sin( np.linspace(self.carrier_phase, 2*pi * carrier_fx, num=self.samples) + modulator)

            self.fm_phase = (2*pi * mod_fx) % (2*pi)
            self.carrier_phase = (2*pi * carrier_fx) % (2*pi)

            self.envelope(self.channel2)
            self.rescale(self.channel2)


    def write_data(self):
        '''stacks channel arrays and resets channel attributes
        writes data to open wave file

        '''
        # stack channels and reassign
        # reset channel objects
        try:
            data = np.stack((self.channel1, self.channel2), axis=1)
        except ValueError:
            if self.channel1 != None:
                data = self.channel1
            else:
                data = self.channel2
        self.channel1 = None
        self.channel2 = None
        self.rand_samples = 0
        
        # write to file
        self.wav.writeframes( np.short(data) )



if __name__ == "__main__":
    t0 = time.time()
    
    comp = Synth(_is_random=True,)
    for _ in range(25):
        comp.sine_generator()
        comp.fm_generator()
        comp.write_data()
    comp.wav.close()
    
    print('%.2f' % ((time.time() - t0) * 1000), 'ms')
    print('output directory:', os.getcwd())