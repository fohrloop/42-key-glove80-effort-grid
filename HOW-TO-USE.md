
# Overview

These are the most important part of this repo. CLI tools:


```
effort_grid_record --help
effort_grid_show --help
```

In addition, the `effort.keyboard.estimate_bias` can be used to estimate bias from the home key sequence.


# Effort calculations

The effort there means purely timing (no: comfort). The effort calculations calculate the average time used to press a key normalized in such way that the fastest key has effort of 1.0. Effort of 2.0 would mean that the effort is exactly twice of the lowest possible effort.

## Usage

To record effort grid, use the effort grid recorder executable:

```
effort_grid_record <config> <outfile>
```

Be aware that recording takes a long time: 42 keys with 10 trigrams each (420 trigrams) and 7 repetitions per trigram takes about 6.5 hours of active typing. 

In addition to that, you need to estimate the bias caused by the left and right home row sequence. This is not automated. You have to run, for example:

```
from effort.keyboard import estimate_bias
estimate_bias(20, 'lkj')
estimate_bias(20, 'sdf')
```

This repeats the chosen sequence 20 times and calculates the average used time (divided by two, as each time the time is recorded twice). You need to add that into the effort config yaml file as `home_key_sequence_timing_left` and `home_key_sequence_timing_right`, for example:

```yml
home_key_sequence_timing_left: 0.212
home_key_sequence_timing_right: 0.223
```

To show the effort grid results in the command line, use

```
effort_grid_show <config> <recorded-file>
```

## FAQ
Q: What is the unit of the effort?

A: The effort is _relative time_, or time relative to the "easiest" key. The easiest key always has effort of 1.0. All other keys always have effort >= 1.0. If your trigram keys have efforst 1.0, 1.4 and 2.0, typing the trigram is expected to take roughly 1.0+1.4+2.0 = 4.4 times as much as typing the easiest key. This obviously has some variance depencing in the order if the characters (which matters a lot!) but on average that should be the case.

Q: Does absolute time matter when recording?

A: No. But you have to be "equally fast" in all of the trigrams; do not change your typing "mode"/speed.

Q: Can I append data to record files?

A: Yes, manually (or using a custom script). The format is pretty self-explanatory (each line has a trigram and the recorded timings in seconds).

## The process

- You most likely you need to temporarily change your keyboard mapping.
- On each key you want to use in effort calculations, you must have a single character like alpha, number or symbol. Exceptions: Do NOT use any symbol which requires SHIFT normally (it will mess up pynput, as you might see Shift down, ? Down, Shift Up, - Up, and the program thinks you have "?" pressed down forever). Also do not use any dead keys like `¨`.
- Create a effortconf.yaml file with your configuration (copy from the [template](effortconfig.yaml))
- Start the effort recording. It will take a while to type each trigram (about 6.5hrs)
- After the recording is done, a raw recording file is saved.
- Get estimates for `home_key_sequence_timing_left` and `home_key_sequence_timing_right` with `effort.keyboard.estimate_bias`
- Use the raw recording file to calculate estimated effort.


## Effort calculations configuration

The configuration is in a single YAML file, like this:

```yml
left:
    pinky: "123qaz"
    ring: "wsx"
    middle: "edc"
    index: "rfvtgb"
    thumb: "789"
right:
    thumb: "`+="
    index: "yhnujm"
    middle: "ik,"
    ring: "ol."
    pinky: "p;/456"

home_key_sequence_left: sdf
home_key_sequence_right: lkj

# The amount of random trigrams to generate per character
trigrams_per_char: 10

trigram_repeat_times: 7

###############
# Calculations
# -------------

# How many (best) timings fromm each trigram to use in calculations
trigram_use_n_best: 3

# Recorded with effort.keyboard.estimate_bias
home_key_sequence_timing_left: 0.212
home_key_sequence_timing_right: 0.223
```

# How the effort is calculated?
The timings are calculated from trigrams (sequence of 3 key presses). Before each recording, you have to type a home key sequence (left or right), which is defined in the configuration as `home_key_sequence_left` and `home_key_sequence_right`. After the last key of the home key sequence is released, the time starts. Then, you type the trigram and repeat the home key sequence. After the last key of the home key sequence is released, the timer stops. The common bias in the recorded times (time required to type the home key sequence) is removed in the calculations. The reason for typing the home key sequence is that it forces you to start from a resting position (no cheating), and this takes account the unbalancing caused by the trigram; if the trigram causes your hands to be off the home position, there is timing penalty as you must then come back to the home row.

The reasons why _trigrams_ are used, because when you type, your fingers are coming from some starting position (=trigram key 1), landing to some key (=trigram key 2) and continuing to some other key (=trigram key 3); they catch timing information better than bigrams. Longer ngrams would be also okay but would require more effort and there's higher chance of mistyping.

## The effort model

The effort model (one model per hand) is 

```
effort = a_1*x_1 + a_2*x_2 + ... a_n*x_n
```

where:

- `effort` is effort (=time in seconds) required for the trigram; Recorded time minus `home_key_sequence_timing_left` or `home_key_sequence_timing_right` 
- `a_i` is the effort coefficient for key `i`. The key `i` runs through all the keys from key number 1 to key number n (=n number of keys for the hand). The unit of the coefficient is seconds.
- `x_i` is equal to 1 if the key `i` is included in the trigram, and 0 otherwise. 
- The key `i` can be any single symbol: alpha letter, number of symbol, or even space character, but it can not be dead key. Each key must output a single, unique character in order of this to work (you may have to change your layout if you have a read key like `¨` on keys you're interested in)
- With this model it is possible to take use every trigram containing key `K`; you may utilize the data from trigrams`ABK`, `KBA` in addition to `AKB`, `CKD`, etc. for key `K`. (less typing for collecting data)

### Example: Using effort model

*This is not necessarily used anywhere but might help you understand what the effort model is.*

The effort model could be used to estimate time required for trigram `<i><j><k>`, where each of the `i`, `j` `k` are numbers from 1 to n and define a key. For example, if `i=5`, `j=6` and `k=1` and all keys (left+right concatenated) are `qwertyasdfghzxcvbuiopåjklöä'nm,.-`, the keys would be  `t`, `y` and `q` and the trigram would be `tyq`, and the estimated effort would be

```
effort_tyq = a_5 + a_6 + a_1
```

where `a_5` is effort for `t`, `a_6` is effort for `y` and `a_1` is effort for `q`. 

### Normalized effort

After effort has been calculated for each key, the minimum effort is 

```
mineff_left = min(a_1, a_2, ... a_n)_left
mineff_right = min(a_1, a_2, ... a_n)_right
mineff = min(mineff_left, mineff_right)
```

and normalized effort A for key `i` is then:

```
A_i = a_i/mineff
```

This means that the key of least effort has always effort of 1.0 and other keys have always effort if `A_j >= 1.0` (`j != i`).