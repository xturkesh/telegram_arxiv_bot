TOKEN = '1154528957:AAHhvlGhaDeR86Fq5Hxyj6ljLtgxIYISvkg'
PATH = 'https://arxiv.org/'
OPTIONS ={'searchtype':'all',
          'abstracts':'show',
          'order':'-announced_date_first',
          'size':'100'}
ABSTRACT='https://arxiv.org/abs/'
DOI = 'https://doi.org/'
BIB_INFO = {'title','date','arxiv_id','pdf_url','abstract'}

START= ("I can provide you ArXiv papers daily. You just "
      "need to tell me the archives I look into, and a set of relevant keywords. \n"
      "My godfather is @archxh. You can ask him for "
      "bugs, suggestions, whatever.\n\n"

      "You can control me through these commands:\n"
      "/help - shows these instructions\n"
      "/list - shows the keyword list\n"
      "/add - add new keyword\n"
      "/remove - remove a keyword\n"
      "/get - get the updates\n"
      "/archive - add or remove arxivs where to look.\n\n\n"
      "Default - writing to the bot replies with a arxiv search query.\n"
      "Last update: 2021/06/02\n\n\n"
      )

TITLE= '-'*30+'\n*ArXiv new entries* -- page {} \n'+'-'*30+'\n'
ARCHIVES =  {'Astrophysics': '/list/astro-ph/new',
             'Condensed Matter': '/list/cond-mat/new',
             'General Relativity and Quantum Cosmology': '/list/gr-qc/new',
             'High Energy Physics - Experiment': '/list/hep-ex/new',
             'High Energy Physics - Lattice': '/list/hep-lat/new',
             'High Energy Physics - Phenomenology': '/list/hep-ph/new',
             'High Energy Physics - Theory': '/list/hep-th/new',
             'Mathematical Physics': '/list/math-ph/new',
             'Nonlinear Sciences': '/list/nlin/new',
             'Nuclear Experiment': '/list/nucl-ex/new',
             'Nuclear Theory': '/list/nucl-th/new',
             'Physics': '/list/physics/new',
             'Quantum Physics': '/list/quant-ph/new',
             'Mathematics': '/list/math/new',
             'Computer Science': '/list/cs/new',
             'Quantitative Biology': '/list/q-bio/new',
             'Quantitative Finance': '/list/q-fin/new',
             'Statistics': '/list/stat/new',
             'Electrical Engineering and Systems Science': '/list/eess/new',
             'Economics': '/list/econ/new'}
SEARCH_MARKUP= {
                 'inline_keyboard': [[
                 {
                     'text':'<<',
                     'callback_data': '<<'
                 },
                 {
                     'text': '<',
                     'callback_data': '<'
                 },
                 {
                    'text': '>',
                    'callback_data': '>'
                 },
                 {
                    'text': '>>',
                    'callback_data': '>>'
                 }
                 ]]}
