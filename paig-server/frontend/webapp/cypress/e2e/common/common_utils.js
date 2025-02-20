var commonUtils = {};
commonUtils.generateRandomWord = (length=5) => {
    const alphabet = 'abcdefghijklmnopqrstuvwxyz';
    let word = '';
    for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * alphabet.length);
        word += alphabet[randomIndex];
    }
    return word;
}

commonUtils.generateRandomSentence = (wordsCount, wordLength) => {
    let sentence = '';
    for (let i = 0; i < wordsCount; i++) {
        sentence += commonUtils.generateRandomWord(wordLength) + ' ';
    }
    return sentence.trim();
}

export default commonUtils;