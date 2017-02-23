import enchant

class SpellingReplacer(object):
    def __init__(self, dict_name='en_US'):
        self.spell_dict = enchant.Dict(dict_name)

    def replace(self, word):
        if self.spell_dict.check(word):
            return word
        suggestions = self.spell_dict.suggest(word)
        return suggestions[0]	#returning the first


#replacer = SpellingReplacer()
#print(replacer.replace("cookbok"))
