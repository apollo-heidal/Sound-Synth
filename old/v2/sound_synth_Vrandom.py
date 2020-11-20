'''sound synthesizer v2
added class Muse()
'''
import numpy as np
import time, random

class Muse:
    def __init__(self):
        self.filename = 'n/a'
        self.fundamental_fx = 55
        self.num_fx = 20
        self.fx_list = None
        self.fs_and_amps = {}
        self.duration = 60
        self.sampling_rate = 44100
        self.nyquist = int( self.sampling_rate / 2 )
        self.data = np.zeros( self.duration * self.sampling_rate )


    def get_random_frequencies(self):
        self.fx_list = random.sample(range(self.fundamental_fx, self.nyquist), self.num_fx)
        self.fx_list.sort()

    
    def get_random_envelope(self):
        for fx in self.fx_list:
            control_points = random.randint(1,self.num_fx)
            self.fs_and_amps[fx] = []
            for _ in range(control_points):
                self.fs_and_amps[fx].append([random.random(), random.random()])
            self.fs_and_amps[fx].sort()


    def make_sine_tone(self, fx):
        return np.sin(np.linspace(0, (2*np.pi * fx), num=( self.duration * self.sampling_rate )))
        

    def apply_envelope(self, sine_tone, cp):
        ts = sine_tone.shape[0]
        for i in range(len(cp) - 1):
            t0 = int(cp[i][0] * ts)
            t1 = int(cp[i + 1][0] * ts)
            a0 = cp[i][1]
            a1 = cp[i + 1][1]
            envelope = np.sin(np.linspace(a0, a1, num=t1-t0))
            sine_tone[t0:t1] += envelope
        return sine_tone


    def synthesize(self):
        for fx in self.fx_list:
            sine_tone = self.make_sine_tone(fx)
            self.data += self.apply_envelope(sine_tone, self.fs_and_amps[fx])


    def amplify(self):
        data_max = np.amax(self.data)
        data_min = np.amin(self.data)
        self.data *= ( (2**16 - 1) / (data_max - data_min) * 0.7)


    def writeWave(self):
        import wave, os
        if self.filename == 'n/a':
            self.filename = 'test.wav'
            w = wave.open(self.filename, 'w')
        else:
            w = wave.open(self.filename, 'w')
        w.setnchannels(1)
        w.setframerate(self.sampling_rate) 
        w.setsampwidth(2)  # N bytes per sample
        w.setnframes(self.data.shape[0])
        w.writeframes(np.short(self.data))
        w.close()
        print('\nOutput file: ' + self.filename + '\n')


if __name__ == "__main__":
    t0 = time.time()
    muse = Muse()
    muse.get_random_frequencies()
    muse.get_random_envelope()
    muse.synthesize()
    muse.amplify()
    muse.writeWave()
    
    print('time elapse: %.2f ms' % ((time.time()-t0) * 1000 ))