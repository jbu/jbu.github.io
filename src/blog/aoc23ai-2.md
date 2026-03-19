---
title: Advent of Code - AI edition - Day 2
date: 2024-03-14
authors: James Uther
---

Each year I get to December and Advent of Code pops up, but coding is my day job so to spice things up I try and add a wrinkle, like \"let\'s do it in the new hotness language\" or whatever. Then by day 4 I get too busy and it all slips, so this could be short. (later: very short and delayed, but will publish as I try and catch up.)\
This year the wrinkle is that I\'m not going to do it. I\'m going to get some AI to do it. I\'m a year behind in doing this so have some existing work to learn from, and i\'ll see what I find.

## Day 1

### Question 1

https://adventofcode.com/2023/day/2:

given

```
Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
```

which game is possible if we have only 12 red cubes, 13 green cubes, and 14 blue cubes? Sum the IDS, and in this case games 1,2,5 are possible so the sum is 8. How about if we ahve 12 red cubes, 13 green cubes, and 14 blue cubes Attempt 1) Chatgpt gets stuck on the example and keeps giving that result. Google Gemini Advanced writes some python code that doesn\'t run. \[\...\] lines of text; each line originally contained a specific calibration value that the Elves now need to recover. On each line, the calibration value can be found by combining the first digit and the last digit (in that order) to form a single two-digit number.\
For example:


    1abc2
    pqr3stu8vwx
    a1b2c3d4e5f
    treb7uchet

In this example, the calibration values of these four lines are 12, 38, 15, and 77. Adding these together produces 142.

### How it went:

I first tried to use Copilot, but it wasn\'t really a big leap, and anyway let\'s push the paradigm. So I just asked chatgpt4:

A document consists of lines of text; each line originally contained a specific calibration value. On each line, the calibration value can be found by combining the first digit and the last digit (in that order) to form a single two-digit number. For example:


      1abc2
      pqr3stu8vwx
      a1b2c3d4e5f
      treb7uchet
      

In this example, the calibration values of these four lines are 12, 38, 15, and 77. What is the value of all of these added together?

\--\> ChatGPT

The total of the calibration values from the given lines is 142. This is calculated by extracting the first and last digit from each line, combining them to form a two-digit number, and then summing these values across all lines.

It wrote some code to do the analysis:

```

  # Given lines with calibration values
  lines = [
      "1abc2",
      "pqr3stu8vwx",
      "a1b2c3d4e5f",
      "treb7uchet"
  ]
  
  # Function to extract calibration values from a line
  def extract_calibration_value(line):
      # Extracting the first and last digit from each line
      first_digit = next((char for char in line if char.isdigit()), None)
      last_digit = next((char for char in reversed(line) if char.isdigit()), None)
      
      # Combining the digits to form a two-digit number
      if first_digit and last_digit:
          return int(first_digit + last_digit)
      else:
          return 0
  
  # Calculating the total calibration value
  total_calibration_value = sum(extract_calibration_value(line) for line in lines)
  total_calibration_value
```

Here\'s a file with a longer document in the same format. Repeat the analysis for this document. (input file uploaded)

\--\> ChatGPT

The total of the calibration values from the document provided in the file is 54,951. This was calculated by extracting the first and last digit from each line, forming two-digit numbers, and summing these values across all lines in the document. ​​

<https://chat.openai.com/share/d50970b5-5d30-45a8-aa30-2dbf042f1200>

### Thoughts

Well that was smooth. Let\'s see how we progress!

### Question 2

Your calculation isn\'t quite right. It looks like some of the digits are actually spelled out with letters: one, two, three, four, five, six, seven, eight, and nine also count as valid \"digits\". Equipped with this new information, you now need to find the real first and last digit on each line. For example:


    two1nine
    eightwothree
    abcone2threexyz
    xtwone3four
    4nineeightseven2
    zoneight234
    7pqrstsixteen

In this example, the calibration values are 29, 83, 13, 24, 42, 14, and 76. Adding these together produces 281. What is the sum of all of the calibration values?

### Process:

Prompt: A document consists of lines of text; each line originally contained a specific calibration value. On each line, the calibration value can be found by combining the first digit and the last digit (in that order) to form a single two-digit number. Some of the digits are actually spelled out with letters: one, two, three, four, five, six, seven, eight, and nine also count as valid \"digits\". For example:


      two1nine
      eightwothree
      abcone2threexyz
      xtwone3four
      4nineeightseven2
      zoneight234
      7pqrstsixteen

In this example, the calibration values are 29, 83, 13, 24, 42, 14, and 76. What is the value of all of the callibration values added together?

\-\--\> ChatGPT\
The total value of all the calibration values added together is 211.

This is wrong. Hooo, boy. I\'m not out of a job yet. I won\'t paste the chat as it\'s long, but you can follow the link below. It didn\'t get the right answer at first, and so I prompted it to start looking at intermediate results. More incorrectness but I could then point to a logical error (it tried to substitute spelled numbers from one-nine, but there are overlaps so that doesn\'t work) so it had another go. Another logical error (the reverse problem, nine-one). I suggested a way forward, and it made it (and was over-obsequious.) It\'s solution was to find the digits with


        re.findall('|'.join(word_to_digit.keys())
      

Which worked for the small set. Huzzah! But then failed for the big set.

I then had to decide how to debug. I was trying to do this \'in character\' with CGPT as an agent writing the code, so I didn\'t want to look at the python. In the end I started to revert to manual inspection of results, starting from the top. Interestingly CGPT was pretty good at this (show me the first 5 lines and results in the form xxxx. Show me the next 10. etc). But nothing sprang out.

In the end I cheated. I solved it myself, grabbed the python from CGPT and compared their outputs to find a line that differed. From there we could work out that the findall above doesn\'t work in all cases, and how to work around it.

<https://chat.openai.com/share/889fc087-9bd4-4cc1-8e72-c90c27fee561>

### Thoughts

This was more interesting. I can see that I was anthropomorphising at times, trying to help a new student through a problem. I like to at least stay polite (good practice) but I can see there\'s going to be a process of learning prompting tricks, and to not unwittingly assume sentience.
