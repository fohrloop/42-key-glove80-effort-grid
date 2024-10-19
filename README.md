# 42 key effort grid for Glove80

## Introduction

The results on this page are timings on a 42-key setup on Glove80 (on "upper thumb key row"). The used layout is 

```
1qwert       uyiop4
2asdfg       hjklö5
3zxcvb       nm,.-6
     789   =+§

```
- Pictures use US alternatives ";/\`" instead of the "ö-§" which are used in data files.

## How these were recorded?

The trigram timings were recorded with the `effort_grid_record` CLI tool (See: [HOW-TO-USE](HOW-TO-USE.md)). For each of the 42 keys on the keyboard, 10 random trigrams were used. Rules for trigram selection: each character on a trigram must correspond to different finger, and each trigram must be unique. Recording each trigram was repeated *7 times*. 


 The timing recording process for each trigram was:
 - First type the *Home Key Sequence* (SDF or LKJ). Time timer starts when the last key was pressed down and at least one key was released after it.
 - Type trigram (three characters)
 - Repeat Home Key Sequence (SDF or LKJ). The timer ends when the last key of the sequence was pressed and at least one key was released after it.

The home key sequence was used to that the starting and ending point is on home row, and it also gave basis for timing. On each trigram, I practiced a bit before any trials to make the key location to be the dominant factor (and not my memory). In summary, there are timings for 420 trigrams and 2940 recorded timings, and the recording process took 6.5 hours.

## Trigram timings

The raw data results are shown in [raw-trigram-timings.txt](raw-trigram-timings.txt). From each 7 repetitions, 3 best times were used. The averages of each three best timings are stored in [average-trigram-timings.txt](average-trigram-timings.txt)  for convenience.

Note that there is bias for each trigram timing coming from the Home Key Sequence. That bias was estimated with `effort.keyboard.estimate_bias` to be roughly 0.212 seconds with left and 0.223 with right hand. The trigram files mentioned above still contain the bias in the timings.

## Trigram timings: Center characters

If you only consider the middle character of each trigram, you get 10 recordings per character. Taking simply the average time for each character and subtracting the bias (~220ms), and normalizing by dividing with smallest timing (295 ms) you will get:

![](timing-averages-center-glove80.svg)

### Comments
- There's not much structure in this
- The sample size is quite small. Only 10 trigrams per character


<details>
<summary>The command used</summary>

```
effort_grid_show effortconfig.yaml raw-trigram-timings.txt --type=average-center
```
</details>


## Trigram timings: All characers of trigram

If timing for each character is calculated as the average of all timing for all trigrams containing the character (at any position; not just middle)  you get more recordings per character. 

After subtracting the bias (~220ms) and normalizing by dividing with smallest timing (372 ms) you will get:

![](timing-averages-glove80.svg)

### Comments
- This shows a bit more structure: All trigrams with thumb or index finger seem to be faster to type.
- Inner keys (index finger) are faster to type than outer keys (pinky)
- Pinky upper key is terrible
- The home keys are not as fast as I would have guessed. Especially middle finger. More on that later.
- The sample sizes are a bit bigger; from 16 to 49 trigrams per character, and 30 on average. See: [sample-sizes.txt](sample-sizes.txt).

<details>
<summary>The command used</summary>

```
effort_grid_show effortconfig.yaml raw-trigram-timings.txt --type=average
```
</details>



## Character Timings: Linear model


I thought this would be the most accurate way of getting the timings information. I've written some explanations in the [HOW-TO-USE.md](HOW-TO-USE.md)

The idea is to use simple model that estimates the timing of **each character** (the two previous attempts show timing of the whole trigram containing the character). So in essence, for each trigram timing, split the timing to the three characters using a model ([sklearn.linear_model.LinearRegression](https://scikit-learn.org/1.5/modules/generated/sklearn.linear_model.LinearRegression.html)).


Again, the bias (~220ms depending on hand) was removed and then results were normalized to 1.0 (1.0 means 75 ms in real life). The resulting heatmap is:

![](relative-effort-glove80-measured.svg)

### Comments
- This heatmap has the clearest structure
- Thumb keys are really fast
- The **index fingers** are also considered really fast -- even the inner columns. 
- The **Home Row** (expect for index finger) is much slower than I thought. One guess for this is the _recording setup_ used: I used the Home Key Sequence SDF or JKL or start and end the recording. If the _trigram_ in question also contained character(s) from the home key sequence, it might made it more difficult (lot's of same keys with varying directions). Try, for example to type as fast as possible: LKJ KLJ LKJ. It would be easier to type KLJ isolated from the LKJ's, but then there should be another solution to start the recording. Perhaps the recording start should have accepted the Home Key Sequence in _any order_? **EDIT: I'm not conviced that this is the reason. The trigram KLJ one of the fastest timings for the character `K`. There must be some other reason. Perhaps the amount of data is too low and the model is giving a bit bogus numbers..?**
- **Trigram direction**: Another very strong point that I learned is that the _position_  of the key is only a small portion of the overall timing for the trigram. The _direction_ of the trigram has far more effect! I was thinking having random samples would average this effect a lot, but actually the sample size is not so large (16 to 49, averages on 30 trigrams per character). Recording 10 or 100 times larger dataset is not very feasible as this already took 6.5hrs of active typing. If I would record this again, I probably would allow any direction for the given trigram, and always choose the easiest one (give more weight to the key location and less to the trigram directions).
- The sample sizes are again: from 16 to 49 trigrams per character, and 30 on average. See: [sample-sizes.txt](sample-sizes.txt). The trigrams were completely random, but distribution to keys was not even. 
- I don't believe there's such a difference between the different thumb keys in reality. These results say that difference within one cluster the difference can be ~0.4. That gives a good rule of thumb: Any number elsewhere could be also off by that amount easily (because of just worse/better luck with trigram selection for the character)
- I trust the results overall with some grains of salt: The JKL, SDF are probably better than shown here. 

<details>
<summary>The command used</summary>

```
effort_grid_show effortconfig.yaml raw-trigram-timings.txt --type=model
```
</details>


## Other things I learned

- Typing ERZ is much easier than typing ERQ. I really dislike the "same row pinky" Q. Not sure what's the name of this phenomenon.
- I generally **dislike bigrams with pinky+(ring|middle)**.  But the ERQ/ERZ thing is a good example that if the pinky is lower, then **pinky+middle** is okayish.
- **pinky + index**  is surprizingly good. No problems at all. Could be because I can move index finger isolation from other fingers (but moving ring affects also middle and pinky).
- Using a **thumb** in a trigram gives superpowers. Thumbs are _fast_.
- **Index finger inner columns** are surprisingly good. I don't know why they're getting so much hate. One thing affecting here might be the fact that index finger is more "isolated" from other fingers (you can move it without moving other finders)?

## What would be my effort grid? 


- I believe that the effort grid calculated by the linear model are close to what I am experiencing, with some modifications: Home Row keys must get a reduction (the numbers were inflated because of an unknown reason. See above), and by smoothening out the calculated effor a bit since there's still lot of variance (caused by the small sample size).
- The best estimate of the effort grid is, with some iterations using the keyboard and comparing key efforts in practice, while trying to keep loyal to the results from the experiment:

![](my-effort-estimate-glove80.svg)

# The question of middle finger home row timings (K vs I)

> [!IMPORTANT]
> This is still bugging me a bit. I did not solve this mystery yet. It might indicate that the model is giving a bit bogus numbers. I would not trust the model's output before this is solved.

There are 43 measurements with K:

<details>
<summary><b>cat average-trigram-timings.txt | grep k | sort -k2,2n</b>
</summary>

```
❯ cat average-trigram-timings.txt | grep k | sort -k2,2n
§hk 0.5078535783298624
§jk 0.5193973659964589
jkl 0.5492664276583431
klj 0.591930644994136
§nk 0.592357423020682
+kl 0.5966128230211325
=uk 0.5976249620046777
ky= 0.6003703476550678
mk§ 0.602232264005579
kml 0.6038062130101025
=kn 0.6053908346802928
kl+ 0.6115938759952163
ylk 0.611837943647212
k+h 0.6134183033330677
omk 0.6173456133304475
+yk 0.6174143436558855
ky§ 0.6460785029921681
kö+ 0.6556130946652653
4jk 0.6693809363253725
+kj 0.672752087994013
k+6 0.6748615493415855
k5o 0.6749727553493964
=6k 0.6770412426752349
+ku 0.6899417073388273
k5= 0.6901330800222544
k-h 0.7041421993441569
n§k 0.7045189943358613
k§j 0.706804696645122
lmk 0.7165621710009873
k6§ 0.7166684909995334
k5. 0.7203691006676914
.kh 0.7221264576655813
k=n 0.7449917640187778
mk4 0.7501215936499648
4+k 0.7830826693292087
ko- 0.8003413013648242
pk§ 0.8176460096534962
lök 0.8546019973582588
.5k 0.8770606613252312
opk 0.8892254573487056
hkö 0.8948065176761398
.pk 0.9117997803259641
4.k 0.9152629169790695
```
</details>

and 40 measurements with I:

<details>
<summary><b>cat average-trigram-timings.txt | grep i | sort -k2,2n</b>
</summary>

```
❯ cat average-trigram-timings.txt | grep i | sort -k2,2n
iu= 0.5125023103319108
=hi 0.540229337348137
+-i 0.5601546539886234
ih§ 0.5671301760012284
iö= 0.569606945985773
oji 0.569836288341321
li+ 0.569951263993668
iuo 0.5732513333205134
§ni 0.5901011480018497
ohi 0.6069101490041552
j+i 0.6070099719994081
i4h 0.6094807036570273
li= 0.6227369119878858
.§i 0.6255014310202872
iyo 0.6256425950171737
-i+ 0.6265600816889977
=pi 0.6267203283302175
ijö 0.6314698706652658
§io 0.6449428463432317
m4i 0.6458953589899465
i6= 0.6475057993472243
i4= 0.6476094469932528
öni 0.6477141409995966
i5. 0.6484479923383333
ipy 0.6625028766575269
i4n 0.6633875853537271
uöi 0.6644145489941972
=i5 0.6672150800004601
hi. 0.6704396629938856
4iu 0.670461720689976
i§4 0.685094406362623
.öi 0.7352586483272413
i=n 0.7420475813754214
li6 0.7447036693338305
i6. 0.7570113556769987
4i. 0.8128276276790226
oip 0.8166151696738476
.6i 0.8177271733099284
-.i 0.8751787379733287
o6i 0.9244920573352525
```
</details>


Why does the model think that `I` so much faster to type than  `K`? The trigrams with I and trigrams with K have almost the same average speeds (See: "Trigram timings: All characers of trigram" -section, 1.18 for `I` and 1.26 for `K`), but the model thinks that the key `K` is 1.53 (=2.64/1.73) times slower to type.. why?

Here are the trigrams for `K` and `I` colored with the used time (blue: fast, red: slow, same color scale for both):

![](effort-K-vs-I.svg)