def check_level(listas)->bool:
    """helper function prevents the list from breaking at character level"""
    for l in range(len(listas)):
        if not isinstance(listas[l],list):
            return False
    return True

def custom_flat(lists:list, level:int) -> list:
    """Transforms a list of string lists into a simpler list based on the specified level.
        lists parameter is the list of lists.
        level is the desired depth of the list.
        It's important to note that this function is influenced by the "shallowest depth" value. 
        That is, when the function finds a string, it will stop flattening values. 
        This format is important for preserving the integrity of the data being scraped.
        ."""
    try:
        for i in range(level):
            if check_level(lists):
                lists = [el for lista in lists for el in lista]
    except Exception as e:
        if e._str_() == "'int' object is not iterable":
            custom_flat(lists, level-1)
            print(e)
        else:    
            print(e._str_())
    return lists
