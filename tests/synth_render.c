#include <AudioToolbox/AudioToolbox.h>
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include "macos_synth.c"

static double render_seconds(HLSynth *synth, unsigned seconds, double *rms) {
    float buffer[512];
    unsigned remaining = seconds * 48000;
    double peak = 0.0, squares = 0.0;
    while (remaining) {
        unsigned frames = remaining < 256 ? remaining : 256;
        assert(hl_synth_render(synth, buffer, frames) == noErr);
        for (unsigned i = 0; i < frames * 2; ++i) {
            assert(isfinite(buffer[i]));
            double value = fabs(buffer[i]);
            if (value > peak) peak = value;
            squares += value * value;
        }
        remaining -= frames;
    }
    *rms = sqrt(squares / (seconds * 48000 * 2));
    return peak;
}

int main(void) {
    HLSynth *synth = NULL;
    assert(hl_synth_open(NULL) != noErr);
    OSStatus status = hl_synth_open(&synth);
    if (status) { fprintf(stderr, "open: %d\n", status); return 1; }
    float unused[2] = {42.0f, 42.0f};
    assert(hl_synth_render(synth, NULL, 0) == noErr);
    assert(hl_synth_render(synth, NULL, 1) != noErr);
    assert(hl_synth_render(synth, unused, 4097) != noErr);
    assert(unused[0] == 42.0f && unused[1] == 42.0f);
    double rms;
    double peak = render_seconds(synth, 5, &rms);
    printf("idle 5s peak=%.8f rms=%.8f timestamp=%.0f\n", peak, rms, synth->sample_time);
    const unsigned char volume[] = {0xb0, 7, 100};
    const unsigned char expression[] = {0xb0, 11, 127};
    const unsigned char note[] = {0x90, 60, 100};
    assert(hl_synth_send(synth, volume, sizeof(volume)) == noErr);
    assert(hl_synth_send(synth, expression, sizeof(expression)) == noErr);
    assert(hl_synth_send(synth, note, sizeof(note)) == noErr);
    peak = render_seconds(synth, 1, &rms);
    printf("note after idle peak=%.8f rms=%.8f timestamp=%.0f\n", peak, rms, synth->sample_time);
    assert(peak > 0.001 && rms > 0.0001);
    hl_synth_close(synth);
    assert(hl_synth_open(&synth) == noErr);
    render_seconds(synth, 5, &rms);
    const unsigned char bank_msb[] = {0xb0, 0, 124};
    const unsigned char bank_lsb[] = {0xb0, 32, 1};
    const unsigned char program[] = {0xc0, 9};
    assert(hl_synth_send(synth, bank_msb, sizeof(bank_msb)) == noErr);
    assert(hl_synth_send(synth, bank_lsb, sizeof(bank_lsb)) == noErr);
    assert(hl_synth_send(synth, program, sizeof(program)) == noErr);
    assert(hl_synth_send(synth, volume, sizeof(volume)) == noErr);
    assert(hl_synth_send(synth, expression, sizeof(expression)) == noErr);
    assert(hl_synth_send(synth, note, sizeof(note)) == noErr);
    peak = render_seconds(synth, 1, &rms);
    printf("bank 124/1 program 9 after idle peak=%.8f rms=%.8f\n", peak, rms);
    assert(peak > 0.001 && rms > 0.0001);
    hl_synth_close(synth);
    hl_synth_close(NULL);
    puts("PASS: idle-to-note output, sample clock, argument boundaries");
    return 0;
}
