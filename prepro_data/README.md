Original Data:

https://github.com/thunlp/DocRED
https://biocreative.bioinformatics.udel.edu/media/store/files/2016/CDR\_Data.zip
https://bitbucket.org/alexwuhkucs/\mbox{gda-extraction}/get/fd4a7409365e.zip


Data Format:
{
  'title',
  'sents':     [
                  [word in sent 0],
                  [word in sent 1]
               ]
  'vertexSet': [
                  [
                    { 'name': mention_name, 
                      'sent_id': mention in which sentence, 
                      'pos': postion of mention in a sentence, 
                      'type': NER_type}
                    {anthor mention}
                  ], 
                  [anthoer entity]
                ]
  'labels':   [
                {
                  'h': idx of head entity in vertexSet,
                  't': idx of tail entity in vertexSet,
                  'r': relation,
                  'evidence': evidence sentences' id
                }
              ]
}
