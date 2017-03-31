import httplib2

"""
This is a quick and dirty function to grab a list of Hong Kong addresses from the Yelp business api
"""

def main():
    h = httplib2.Http()

    tf = open("yelp_business_hk.txt", "w")
    limit = 50
    pagelimit = 5
    for p in range(1,pagelimit):
        offset = p*limit
        r, c = h.request("https://api.yelp.com/v3/businesses/search?term=restaurant&location=hong+kong&limit="+str(limit)+"&offset="+str(offset),
                         "GET",
                         headers={'Authorization' : 'Bearer 7mIGWSL7vyK_gI0shlsqYWlB2nS5SrT-WlhRRiU_YxLk6Rz2AbVIGxq2rWly3vc2fjUdQ-ycmLDUsq9yOUE32oacY8-hSIJd6s38jbGj4ZXosjvooKtUPZmRXQTUWHYx'})
        print r
        tf.write(c+"\n")

    tf.close()

if __name__ == '__main__':
    main()