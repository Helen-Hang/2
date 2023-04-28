# Original Data:
```

> DocRED: https://github.com/thunlp/DocRED

> CDR: https://biocreative.bioinformatics.udel.edu/media/store/files/2016/CDR\_Data.zip

> GDA: https://bitbucket.org/alexwuhkucs/\mbox{gda-extraction}/get/fd4a7409365e.zip

```

# Preprocessing data：
```

> DocRED: https://drive.google.com/drive/folders/1Ovj7PWpi3MLzGawhrpqiRcjVTpHdZfup

> CDR: https://drive.google.com/drive/folders/1VXR1Dmxst4BtOKbYWehhkUTV__5UoHHQ

> GDA: https://drive.google.com/drive/folders/1eNLLJYh9vq8TAGZSNzkpD8h2ddmh3rda

```

# Data Format:
```
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
```






