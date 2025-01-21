import math
import re

class SearchID:
    start_id = 100
    wheel_nums = ['S', '1', '2', '5', '1', '10', '2', '5', '1', '8', '2',
                  'P', '1', '2', '1', '5', '1', '10', '1', '8', '1', '2',
                  'T', '1', '2', '5', '1', '2', '1', '8', '2', '1',
                  'P', '2', '1', '8', '1', '10', '1', '5', '1', '2', '1',
                  'T', '2', '8', '1', '5', '2', '10', '1', '5', '2', '1']
    wheel_class_list = ['1', '10', 'T', '2', 'S', 'P', '5', '8']
    x_low_threshold = 30


    def __init__(self):
        i = self.start_id
        self.sectors = []
        for num in self.wheel_nums:
            s = [num, i]
            self.sectors.append(s)
            i += 1

    def position_sectors(self, det):
        sort_det = reversed(det)[reversed(det)[:, 0].sort()[1]]
        filtered_coord = []
        last_sector_x_x = []
        for *xyxy, conf, cls in sort_det:
            center_x = (xyxy[0] + xyxy[2]) / 2
            center_y = (xyxy[1] + xyxy[3]) / 2
            if len(filtered_coord) > 0:
                if center_x - filtered_coord[len(filtered_coord)-1][0][0] <= self.x_low_threshold:
                    last_x_len = last_sector_x_x[1] - last_sector_x_x[0]
                    new_x_len = xyxy[2] - xyxy[0]
                    if new_x_len > last_x_len:
                        filtered_coord[len(filtered_coord)-1] = [(center_x, center_y), cls]
                else:
                    filtered_coord.append([(center_x, center_y), cls])
                    last_sector_x_x = [xyxy[0], xyxy[2]]
            else:
                filtered_coord.append([(center_x, center_y), cls])
                last_sector_x_x = [xyxy[0], xyxy[2]]
        ids = self.position_det_sectors(filtered_coord)
        self.id_array = []
        for i in range(len(ids)):
            self.id_array.append([filtered_coord[i][0], ids[i], filtered_coord[i][1]])
        return self.id_array

    def position_det_sectors(self, det):
        marked = []
        for d in det:
            print(d[1])
            print(int(d[1]))
            print(str(int(d[1])))
            cls = self.wheel_class_list[int(d[1].item())]
            marked.append(cls)
        for i in range(len(marked)):
            if not marked[i] in ["1", "2", "5"]:
                marked[i] = "?"

        len_marked_ = len(marked) - 1
        joined_wheel = ''.join(self.wheel_nums + self.wheel_nums[:len_marked_])
        joined_marked = ''.join(marked)
        joined_wheel = re.sub('10', '9', joined_wheel)
        reg = re.sub('\?', '[1-9,S,T,P]', joined_marked)
        p = re.compile(reg)
        part_list = re.findall(p, joined_wheel)
        num = len(part_list)
        if num > 1 or num <= 0:
            return -1
        self.start = joined_wheel.find(part_list[0])
        self.count = len(marked)
        res = []
        for j in range(self.start, self.start + self.count):
            i = j
            if j >= len(self.sectors):
                i = j - len(self.sectors)
            id = self.sectors[i][1]
            res.append(id)
        return res

    def find_by_xy(self, xyxy):
        x = (xyxy[0] + xyxy[2]) / 2
        for s in self.id_array:
            if abs(s[0][0] - x) <= self.x_low_threshold:
                return s[1]
        return -1