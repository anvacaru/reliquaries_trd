s.options.blockSize = 1024;
s.options.hardwareBufferSize = 512;

s.waitForBoot(onComplete: {
	
//	{ Out.ar(0, SinOsc.ar(220, 0, 0.5) ) }.play;
	

	//s.freeAll;
	//s.freeAllBuffers;
	//s.sync;

	SynthDef(\son, { | out = 1, dist = 100, himidity = 50, temp = 25, gate = 1, rec_time = 10 |

		// var buf = LocalBuf.new(8);
		var change = \change.tr(-1);
		// var buf = LocalBuf.new(8, 4);
		var buf = LocalBuf.new(8, 1);
		
		var amp =  \amp.kr(0, 0.1, true).linlin(0.2, 0.56, 0.1, 1);
		var freq = \freq.kr(50, 0.1, true);
		var lux =  \lux.kr(0, 0.1, true);
		var dur =  \dur.kr(0, 0.1, true);
		var imp = Impulse.kr(rec_time.reciprocal);
		
		var d = lux.linlin(0, 1000, 0, 1);
		var f = freq.linlin(40, 76, 0, 1);
		var h = himidity.linlin(0, 100, 0, 1);
		var t = temp.linlin(5, 35, 0, 1.0);
		
		var c = d + f + h + t; 
		var pos = PulseCount.kr(imp).mod(8);
		var m = BufWr.kr(c, buf, pos, 1); //[1.1, 0.5, 3, 3.3, 0.667, 1.3, 1.75, 4]; //
		var harm = BufRd.kr(1, buf, [0, 1, 2, 3, 4, 5, 6, 7]).abs.lag2(0.5) * [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5];
		/*
		var pos = PulseCount.kr(change).mod(8);
		var m = BufWr.kr([d, f, h, t], buf, pos, 1);
		var harm = 1 + BufRd.kr(4, buf, PulseDivider.kr(Impulse.kr(4.reciprocal), 8)).poll(change);
		*/
		var pulse = EnvGen.ar( Env.asr(0.1, amp, 0.1,  [4, -4]), Trig1.kr(Impulse.kr((dur + d)*amp), 0.5) );
		var env = EnvGen.ar(Env.asr(1, 1, 1), gate);
		var sig1 = Mix.new(SinOscFB.ar(freq * harm, d, (0.1+amp).clip(0, 1.0) ));
		var sig2 = PMOsc.ar(freq * [0.25, 0.5, 1], lux.linlin(0, 300, 10, 200), dur * amp.linlin(0, 1, 1, 9)) * pulse;
		var sig3 = Pulse.ar(freq/2, dur) * pulse * amp;
		var sig = (sig1*0.3) + (sig2*0.3) + (sig3*0.4);
		var final = Mix.new(sig).tanh;

		final = Limiter.ar(FreeVerb.ar( final, mix:0.2, room:0.2, damp:0.9));


		Out.ar(out, HPF.ar(final, 30).dup * env);


	}).add;

	s.sync;

	// ~b = Buffer.alloc(s, s.sampleRate*10, 1); // enough space for one second of mono audio
	s.sync;

	~x = Synth(\son, [\out, 0]);
	
	~last_lux = 0;
	~last_hum = 0;
	~last_temp = 0;
	~last_dist = 0;
	

	// { Out.ar(0, SinOsc.ar(220, 0, 0.5) ) }.play;
	// dist, lux, humidity, temp, vol, pitch, dur
	OSCdef(\sensors, {|msg, time, addr, recvPort|

		var dist = msg[1].asFloat;
		var lux = msg[2].asFloat;
		var humidity = msg[3].asFloat;
		var temp = msg[4].asFloat;
		var vol = msg[5].asFloat;
		var pitch = msg[6].asFloat;
		var dur = msg[7].asFloat;
		var ch = false;
		
		if(~last_lux != lux, { ch = true; ~last_lux = lux});
		if(~last_hum != humidity, { ch = true; ~last_hum = humidity});
		if(~last_temp != temp, { ch = true; ~last_temp = temp});
		if(~last_dist != dist, { ch = true; ~last_dist = dist});
		
		~x.set(\amp, vol.clip(0.0, 1.0) );
		~x.set(\freq, pitch.clip(10, 880));
		~x.set(\dur, dur);
		~x.set(\lux, lux);
		
		
		if(ch, { ~x.set(\change, 1)});
		ch = false;

		// msg.postln;
	}, '/sense'); // def style


	
});
