import json
import os

image_index_path = "/home/liuliu/Research/mara_bench/face-detect/pics/pic_index/training.txt"
pic_path = "/home/liuliu/Research/mara_bench/face-detect/pics/"
evaluation_obj_path = "/home/liuliu/Research/mara_bench/face-detect/evaluation/evaluate"
grond_truth_path = "/home/liuliu/Research/mara_bench/face-detect/pics/pic_index/training_result.txt"

obj_path = '/home/liuliu/Research/mara_bench/face-detect/facedetect'


def getQoS():
    # run the evaluation routine
    evaluate_cmd = [
    evaluation_obj_path,
    '-a',
    grond_truth_path,
    '-d',
    './result.txt',
    '-f',
    '0',
    '-i',
    pic_path,
    '-l',
    image_index_path,
    '-z',
    '.jpg'
    ]
    os.system(" ".join(evaluate_cmd))
    # get the precision and recall
    result = open('./tempDiscROC.txt','r')
    # call evaluate routine
    for line in result:
        col = line.split()
        recall = float(col[0])
        precision = float(col[1])
        break
    print precision, recall

def run(preferences):
    # generate the xml
    cmd = ['python',
           config['rapidScript'],
           '--cfg',
           './facedetect_run.config',
           "--model",
           "piecewise",
           "-m",
           "finalize",
           ]
    os.system(" ".join(cmd))
    # run ferret
    output_name = "custom_outputs/output" + "_" + str(
        preferences[0]) + "_" + str(preferences[1]) + ".txt"
    face_cmd = [obj_path,
                  "-index",
                  image_index_path,
                  '-p',
                  '-rsdg',
                  '-cont',
                  '-xml',
                  './outputs/ferret.xml',
                  '-b',
                  '200',
                  '-u',
                  '100'
                  ]
    print(' '.join(face_cmd))
    os.system(' '.join(face_cmd))

    # check the result
    getQoS()
    # move the xml
    mv_cmd = ['mv',
              './outputs/facedetect.xml',
              './xmls/facedetect' + "_" + str(preferences[0]) + "_" + str(
                  preferences[1]) + ".xml"]
    os.system(" ".join(mv_cmd))


with open('./facedetect_run.config', 'r') as config_json:
    config = json.load(config_json)

for preferences in range(1, 10):
    # relavance from 1 to 10
    config['preferences'][0] = float(1.0 + float(preferences))
    configfile = open('./facedetect_run.config', 'w')
    json.dump(config, configfile, indent=2, sort_keys=True)
    configfile.close()
    run(config['preferences'])
