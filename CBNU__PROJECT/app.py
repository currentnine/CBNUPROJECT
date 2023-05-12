import datetime
import json
import math
import urllib.request
import matplotlib
import matplotlib.pyplot as plt
# 작성된 url에 접속해서 데이터 받아오기
from matplotlib import font_manager
def get_request_url(url):
    req = urllib.request.Request(url)
    # 정보를 받아오는 처리에는 예외가 발생될 수 있으므로 예외 처리
    try:
        response = urllib.request.urlopen(req)  # url 응답
        if response.getcode() == 200:  # 200: url이 동작함/ 400번대 : 정보가 없음, 500번대: 오류가 있음
            # 데이터 성공적으로 불러온 시간
            print("[%s] Url Request Success" % datetime.datetime.now())  # %s: 표현식
            # 데이터 불러오기
            return response.read().decode('utf-8')  # utf-8 형식으로 불러오기
    except Exception as e:  # 에러시 에러 정보 출력
        print(e)
        print("[%s] Error for URL:%s" % (datetime.datetime.now(), url))
        return None
# url에 필요한 정보 입력
def getTourPointVisitor(yyyymm, sido, gungu, nPagenum, nItems):
    # 데이터를 가져올 url 만들기
    # 사용 url
    end_point = "http://openapi.tour.go.kr/openapi/service/TourismResourceStatsService/getPchrgTrrsrtVisitorList"
    # 인증키
    access_key = "서비스키 입력"#본인의 키 입력
    # url 뒤에 넘겨줄 데이터 준비
    parameters = "?_type=json&serviceKey=" + access_`key  # json 파일로 받기
    parameters += "&YM=" + yyyymm
    parameters += "&SIDO=" + urllib.parse.quote(sido)
    # parse.quote(): 한글을 그대로 넣으면 링크가 끝난 것으로 인식하므로 유니코드로 바꿔서 넣기
    parameters += "&GUNGU=" + urllib.parse.quote(gungu)
    parameters += "&RES_NM=&pageNo=" + str(nPagenum)
    parameters += "&numOfRows=" + str(nItems)
    # url + parameter -> 실제적으로 사용할 url 완성
    url = end_point + parameters
    # 데이터 요청
    retData = get_request_url(url)
    if (retData == None):
        return None
    else:
        # 요청한 데이터가 json 문자열로 넘어옴-> json 객체에 넣어 처리하도록 함(loads())
        return json.loads(retData)
# 꺼내온 데이터를 json 형식에 맞추기 - 제공되는 document 참조
def getTourPointData(item, yyyymm, jsonResult):  # item: json의 키값
    # 삼항 연산자 - value값이 없으면 공백, 0 출력. 있으면 value값 출력
    addrCd = 0 if 'addrCd' not in item.keys() else item['addrCd']  # 지역코드
    gungu = '' if 'gungu' not in item.keys() else item['gungu']
    sido = '' if 'sido' not in item.keys() else item['sido']
    resNm = '' if 'resNm' not in item.keys() else item['resNm']  # 관광지
    rnum = 0 if 'rnum' not in item.keys() else item['rnum']  # 결과값 나열 순서 -primary key
    ForNum = 0 if 'csForCnt' not in item.keys() else item['csForCnt']  # 외국인 방문객
    NatNum = 0 if 'csNatCnt' not in item.keys() else item['csNatCnt']  # 내국인 방문객
    jsonResult.append({'yyyymm': yyyymm, 'addrCd': addrCd, 'gungu': gungu,
                       'sido': sido, 'resNm': resNm, 'rnum': rnum, 'ForNum': ForNum,
                       'NatNum': NatNum})
    return
# main() 선언 - 데이터 수집을 위한 정보 설정

def main():
    #main함수
    # 데이터를 가져와서 리스트 변수로 저장
    jsonResult = []  # json 문서로 가져올 것
    # 검색내용 - 서울특별시 전체 구
    sido = "서울특별시"
    gungu = ""
    nPagenum = 1
    nTotal = 0
    nItems = 100
    # 검색 기간 - 2011~2017
    nStartYear = 2011
    nEndYear = 2017
    # 데이터 불러오기
    for year in range(nStartYear, nEndYear - 1):
        # 월에 해당되는 데이터 반복
        for month in range(1, 12 + 1):
            # 형식에 맞는 표현 : {인덱스}.format(0번째 데이터, 1번째 데이터, ... )
            yyyymm = "{0}{1:0>2}".format(str(year), str(month))
        #            print(yyyymm) 데이터 확인
        #            getTourPointVisitor(yyyymm, sido, gungu, nPagenum, nItems)  url 호출
        nPagenum = 1
        while True:
            # url에 데이터 호출
            jsonData = getTourPointVisitor(yyyymm, sido, gungu, nPagenum, nItems)
            if (jsonData['response']['header']['resultMsg'] == 'OK'):  # 데이터가 정상적으로 들어옴
                nTotal = jsonData['response']['body']['totalCount']  # []: dictionary
                if nTotal == 0:  # 들어온 데이터의 개수가 0개
                    break
                # 들어온 데이터의 개수가 1개 이상
                for item in jsonData['response']['body']['items']['item']:
                    getTourPointData(item, yyyymm, jsonResult)
                # 한 페이지당 100 개의 데이터 표시
                nPage = math.ceil(nTotal / 100)  # nPage:전체 페이지, nTotal: 전체 데이터
                if (nPagenum == nPage):  # 페이지 끝까지 감
                    break
                nPagenum += 1  # 페이지 증가
            else:  # 데이터가 들어오지 않음
                break
    # 그래프용 인덱스 만들기- 관광지별 국내 방문객 수
    resNm = []
    NatNum = []
    index = []
    i = 0
    for item in jsonResult:
        if (item['gungu'] == '종로구'):
            index.append(i)
            resNm.append(item['resNm'])
            NatNum.append(item['NatNum'])
            i = i + 1
    # json 파일로 저장
    with open('%s_관광지입장정보_%d_%d.json' % (sido, nStartYear, nEndYear - 1), 'w', encoding='utf8') as outfile:
        # with 블록 : 자원을 사용하고 끝나면 자원 자동 반환
        retJson = json.dumps(jsonResult, indent=4, sort_keys=True, ensure_ascii=False)
        # dumps: 들어온 데이터를 하나의 json 문자열로 만들어줌, indent: 보기 편하게 정렬
        outfile.write(retJson)
    print('%s_관광지입장정보_%d_%d.json SAVED' % (sido, nStartYear, nEndYear - 1))  # 저장 확인
    # 그래프 그리기
    # 한글 처리
    font_location = "C:\Windows\Fonts\gulim.ttc"
    font_name = font_manager.FontProperties(fname=font_location).get_name()
    matplotlib.rc('font', family=font_name)
    plt.xticks(index, resNm)
    plt.plot(index, NatNum)
    plt.xlabel('관광지')
    plt.ylabel('내국인 방문객 수')
    plt.title('2011-2016. 서울특별시 종로구 관광지의 내국인 방문객 수')
    plt.grid(True)
    plt.show()



if __name__ == '__main__':
    #    print(datetime.datetime.now()) 데이터를 가져온 날짜

    main()