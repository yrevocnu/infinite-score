from yaml import safe_load, dump

def clean_bounty_metadata(file_in, file_out):
    """
    Creates an anonymized version of the bounty data that fits the schema expected by
    the yrevocnu.com website.
    """

    bounty_metadata = safe_load(open(file_in))

    clean_bounty_metadata = {}

    def clean_bounty_dict(bd):
        """
        """

        terms = {
            'value' : 'bounty',
            'short' : 'short',
            'long' : 'long',
            'open' : 'open',
            'closed' : 'closed'
        }
    
        cbd = {
            terms[term] : bd[term]
            for term
            in terms
            if term in bd
        }
    
        return cbd

    clean_bounty_metadata = {}

    clean_bounty_metadata['open'] = [
        clean_bounty_dict(bd)
        for bd in bounty_metadata['open']]

    clean_bounty_metadata['closed'] = [
        clean_bounty_dict(bd)
        for bd in bounty_metadata['closed']]

    with open(file_out, 'w') as f:
        f.write(dump(clean_bounty_metadata))
        f.close()