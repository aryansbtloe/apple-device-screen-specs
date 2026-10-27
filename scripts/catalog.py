"""Curated device catalog: which Apple page backs each device, plus facts that are categorical
(home button, cutout, biometrics). Numeric screen values are NOT typed here; build_dataset.py
reads them from the saved Apple pages (sources/parsed_specs.json) and the HIG snapshot."""

S = 'https://support.apple.com/en-us/'

def d(id, name, family, line, year, spec, url, **kw):
    e = dict(id=id, name=name, family=family, line=line, release_year=year, spec=spec, source_url=url)
    e.update(kw); return e

# ---------- iPhone ----------
# hig = exact row name in the HIG "iOS, iPadOS device screen dimensions" table (July 2026 snapshot)
# hig_same_panel = HIG row of a device whose panel Apple lists with identical pixels and ppi (logical size derived)
IPHONE = [
 d('iphone-duo','iPhone Duo','iphone','iPhone',2026,'iphone-301318.txt',S+'148588',wiki='iPhone Duo',cutout='dynamic-island',biometric='face-id',home_button=False,
   secondary_label='cover display', notes=['Foldable. Primary record is the inner folding display; the cover display is under secondary_screens.']),
 d('iphone-18-pro-max','iPhone 18 Pro Max','iphone','iPhone Pro',2026,'iphone-301317.txt',S+'148591',wiki='iPhone 18 Pro Max',hig_same_panel='iPhone 17 Pro Max',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-18-pro','iPhone 18 Pro','iphone','iPhone Pro',2026,'iphone-301316.txt',S+'148590',wiki='iPhone 18 Pro',hig_same_panel='iPhone 17 Pro',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-17e','iPhone 17e','iphone','iPhone e',2026,'iphone-301285.txt',S+'126470',wiki='iPhone 17e',hig_same_panel='iPhone 16e',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-17-pro-max','iPhone 17 Pro Max','iphone','iPhone Pro',2025,'iphone-301246.txt',S+'125091',wiki='iPhone 17 Pro Max',hig='iPhone 17 Pro Max',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-17-pro','iPhone 17 Pro','iphone','iPhone Pro',2025,'iphone-301245.txt',S+'125090',wiki='iPhone 17 Pro',hig='iPhone 17 Pro',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-air','iPhone Air','iphone','iPhone Air',2025,'iphone-301244.txt',S+'125092',wiki='iPhone Air',hig='iPhone Air',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-17','iPhone 17','iphone','iPhone',2025,'iphone-301247.txt',S+'125089',wiki='iPhone 17',hig='iPhone 17',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-16e','iPhone 16e','iphone','iPhone e',2025,'iphone-301076.txt',S+'122208',wiki='iPhone 16e',hig='iPhone 16e',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-16-pro-max','iPhone 16 Pro Max','iphone','iPhone Pro',2024,'iphone-301048.txt',S+'121032',wiki='iPhone 16 Pro Max',hig='iPhone 16 Pro Max',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-16-pro','iPhone 16 Pro','iphone','iPhone Pro',2024,'iphone-301047.txt',S+'121031',wiki='iPhone 16 Pro',hig='iPhone 16 Pro',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-16-plus','iPhone 16 Plus','iphone','iPhone',2024,'iphone-301046.txt',S+'121030',wiki='iPhone 16 Plus',hig='iPhone 16 Plus',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-16','iPhone 16','iphone','iPhone',2024,'iphone-301045.txt',S+'121029',wiki='iPhone 16',hig='iPhone 16',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-15-pro-max','iPhone 15 Pro Max','iphone','iPhone Pro',2023,'iphone-301003.txt',S+'111828',wiki='iPhone 15 Pro Max',hig='iPhone 15 Pro Max',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-15-pro','iPhone 15 Pro','iphone','iPhone Pro',2023,'iphone-300993.txt',S+'111829',wiki='iPhone 15 Pro',hig='iPhone 15 Pro',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-15-plus','iPhone 15 Plus','iphone','iPhone',2023,'iphone-301004.txt',S+'111830',wiki='iPhone 15 Plus',hig='iPhone 15 Plus',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-15','iPhone 15','iphone','iPhone',2023,'iphone-300991.txt',S+'111831',wiki='iPhone 15',hig='iPhone 15',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-14-pro-max','iPhone 14 Pro Max','iphone','iPhone Pro',2022,'iphone-300881.txt',S+'111846',wiki='iPhone 14 Pro Max',hig='iPhone 14 Pro Max',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-14-pro','iPhone 14 Pro','iphone','iPhone Pro',2022,'iphone-300880.txt',S+'111849',wiki='iPhone 14 Pro',hig='iPhone 14 Pro',cutout='dynamic-island',biometric='face-id',home_button=False),
 d('iphone-14-plus','iPhone 14 Plus','iphone','iPhone',2022,'iphone-300879.txt',S+'111854',wiki='iPhone 14 Plus',hig='iPhone 14 Plus',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-14','iPhone 14','iphone','iPhone',2022,'iphone-300878.txt',S+'111850',wiki='iPhone 14',hig='iPhone 14',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-se-3rd-generation','iPhone SE (3rd generation)','iphone','iPhone SE',2022,'iphone-300865.txt',S+'111866',wiki='iPhone SE / (3rd generation)',hig='iPhone SE 4.7-inch',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-13-pro-max','iPhone 13 Pro Max','iphone','iPhone Pro',2021,'iphone-300430.txt',S+'111870',wiki='iPhone 13 Pro Max',hig='iPhone 13 Pro Max',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-13-pro','iPhone 13 Pro','iphone','iPhone Pro',2021,'iphone-300429.txt',S+'111871',wiki='iPhone 13 Pro',hig='iPhone 13 Pro',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-13','iPhone 13','iphone','iPhone',2021,'iphone-300428.txt',S+'111872',wiki='iPhone 13',hig='iPhone 13',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-13-mini','iPhone 13 mini','iphone','iPhone mini',2021,'iphone-300426.txt',S+'111873',wiki='iPhone 13 mini',hig='iPhone 13 mini',cutout='notch',biometric='face-id',home_button=False,mini_conflict=True),
 d('iphone-12-pro-max','iPhone 12 Pro Max','iphone','iPhone Pro',2020,'iphone-300240.txt',S+'111874',wiki='iPhone 12 Pro Max',hig='iPhone 12 Pro Max',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-12-pro','iPhone 12 Pro','iphone','iPhone Pro',2020,'iphone-300242.txt',S+'111875',wiki='iPhone 12 Pro',hig='iPhone 12 Pro',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-12','iPhone 12','iphone','iPhone',2020,'iphone-300241.txt',S+'111876',wiki='iPhone 12',hig='iPhone 12',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-12-mini','iPhone 12 mini','iphone','iPhone mini',2020,'iphone-300239.txt',S+'111877',wiki='iPhone 12 mini',hig='iPhone 12 mini',cutout='notch',biometric='face-id',home_button=False,mini_conflict=True),
 d('iphone-se-2nd-generation','iPhone SE (2nd generation)','iphone','iPhone SE',2020,'iphone-509370.txt',S+'111882',wiki='iPhone SE / (2nd generation)',hig='iPhone SE 4.7-inch',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-11-pro-max','iPhone 11 Pro Max','iphone','iPhone Pro',2019,'iphone-507845.txt',S+'111878',wiki='iPhone 11 Pro Max',hig='iPhone 11 Pro Max',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-11-pro','iPhone 11 Pro','iphone','iPhone Pro',2019,'iphone-507808.txt',S+'111879',wiki='iPhone 11 Pro',hig='iPhone 11 Pro',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-11','iPhone 11','iphone','iPhone',2019,'iphone-507882.txt',S+'111865',wiki='iPhone 11',hig='iPhone 11',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-xs-max','iPhone XS Max','iphone','iPhone X',2018,'iphone-505716.txt',S+'111880',wiki='iPhone XS Max',hig='iPhone XS Max',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-xs','iPhone XS','iphone','iPhone X',2018,'iphone-505753.txt',S+'111881',wiki='iPhone XS',hig='iPhone XS',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-xr','iPhone XR','iphone','iPhone X',2018,'iphone-505602.txt',S+'111868',wiki='iPhone XR',hig='iPhone XR',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-x','iPhone X','iphone','iPhone X',2017,'iphone-504268.txt',S+'111864',wiki='iPhone X',hig='iPhone X',cutout='notch',biometric='face-id',home_button=False),
 d('iphone-8-plus','iPhone 8 Plus','iphone','iPhone Plus',2017,'iphone-504267.txt',S+'111950',wiki='iPhone 8 Plus',hig='iPhone 8 Plus',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-8','iPhone 8','iphone','iPhone',2017,'iphone-504266.txt',S+'111976',wiki='iPhone 8',hig='iPhone 8',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-7-plus','iPhone 7 Plus','iphone','iPhone Plus',2016,'iphone-502287.txt',S+'111953',wiki='iPhone 7 Plus',hig='iPhone 7 Plus',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-7','iPhone 7','iphone','iPhone',2016,'iphone-502272.txt',S+'111943',wiki='iPhone 7',hig='iPhone 7',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-se-1st-generation','iPhone SE (1st generation)','iphone','iPhone SE',2016,'iphone-501343.txt',S+'112005',wiki='iPhone SE / (1st generation)',hig='iPhone SE 4-inch',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-6s-plus','iPhone 6s Plus','iphone','iPhone Plus',2015,'iphone-500040.txt',S+'111996',wiki='iPhone 6s Plus',hig='iPhone 6s Plus',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-6s','iPhone 6s','iphone','iPhone',2015,'iphone-500016.txt',S+'111952',wiki='iPhone 6s',hig='iPhone 6s',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-6-plus','iPhone 6 Plus','iphone','iPhone Plus',2014,'iphone-134710.txt',S+'111940',wiki='iPhone 6 Plus',hig='iPhone 6 Plus',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-6','iPhone 6','iphone','iPhone',2014,'iphone-134711.txt',S+'111954',wiki='iPhone 6',hig='iPhone 6',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-5s','iPhone 5s','iphone','iPhone',2013,'iphone-134096.txt',S+'111973',wiki='iPhone 5s',hig_same_panel='iPhone SE 4-inch',cutout='none',biometric='touch-id',home_button=True),
 d('iphone-5c','iPhone 5c','iphone','iPhone',2013,'iphone-134094.txt',S+'111917',wiki='iPhone 5c',hig_same_panel='iPhone SE 4-inch',cutout='none',biometric=None,home_button=True),
 d('iphone-5','iPhone 5','iphone','iPhone',2012,'iphone-133778.txt',S+'112016',wiki='iPhone 5',hig_same_panel='iPhone SE 4-inch',cutout='none',biometric=None,home_button=True),
 d('iphone-4s','iPhone 4S','iphone','iPhone',2011,'iphone-133476.txt',S+'112004',wiki='iPhone 4s',scale_rule=2,cutout='none',biometric=None,home_button=True),
 d('iphone-4','iPhone 4','iphone','iPhone',2010,'iphone-132927.txt',S+'112562',wiki='iPhone 4',scale_rule=2,cutout='none',biometric=None,home_button=True),
 d('iphone-3gs','iPhone 3GS','iphone','iPhone',2009,'iphone-132537.txt',S+'112307',wiki='iPhone 3GS',scale_rule=1,cutout='none',biometric=None,home_button=True),
 d('iphone-3g','iPhone 3G','iphone','iPhone',2008,'iphone-132035.txt',S+'112496',wiki='iPhone 3G',scale_rule=1,cutout='none',biometric=None,home_button=True),
 d('iphone-1st-generation','iPhone (1st generation)','iphone','iPhone',2007,'iphone-131510.txt',S+'112445',wiki='iPhone',scale_rule=1,cutout='none',biometric=None,home_button=True),
]

# ---------- iPad ---------- (Wi-Fi spec page used; Wi-Fi + Cellular shares the display)
def ip(id,name,line,year,spec,url,wiki,hig=None,same=None,scale_rule=None,cut='none',bio='touch-id',home=True,marketed=None,**kw):
    return d(id,name,'ipad',line,year,spec,url,wiki=wiki,hig=hig,hig_same_panel=same,scale_rule=scale_rule,cutout=cut,biometric=bio,home_button=home,marketed_diagonal_in=marketed,**kw)
IPAD = [
 ip('ipad-mini-a20-pro','iPad mini (A20 Pro)','iPad mini',2026,'applecom-ipad-mini-specs.txt','https://www.apple.com/ipad-mini/specs/','iPad Mini / (A20 Pro)',bio='touch-id',home=False,status='announced',marketed=8.5,
    notes=['Listed on apple.com/ipad-mini/specs; no support.apple.com Tech Specs page or HIG entry yet. Wikipedia marks it as upcoming.']),
 ip('ipad-air-13-inch-m4','iPad Air 13-inch (M4)','iPad Air',2026,'ipad-301283.txt',S+'126472','iPad Air 13-in. (M4)',hig='iPad Air 13-inch',bio='touch-id',home=False,marketed=13),
 ip('ipad-air-11-inch-m4','iPad Air 11-inch (M4)','iPad Air',2026,'ipad-301281.txt',S+'126471','iPad Air 11-in. (M4)',hig='iPad Air 11-inch',bio='touch-id',home=False,marketed=11),
 ip('ipad-pro-13-inch-m5','iPad Pro 13-inch (M5)','iPad Pro',2025,'ipad-301272.txt',S+'125407','iPad Pro 13-in. (M5)',hig='iPad Pro 13-inch',cut='none',bio='face-id',home=False,marketed=13),
 ip('ipad-pro-11-inch-m5','iPad Pro 11-inch (M5)','iPad Pro',2025,'ipad-301270.txt',S+'125406','iPad Pro 11-in. (M5)',hig='iPad Pro 11-inch 5th and 6th generation',cut='none',bio='face-id',home=False,marketed=11),
 ip('ipad-a16','iPad (A16)','iPad',2025,'ipad-301079.txt',S+'122240','iPad (11th generation)|iPad<br />{{Small|(A16)}}',hig='iPad 11-inch',bio='touch-id',home=False,marketed=11),
 ip('ipad-air-13-inch-m3','iPad Air 13-inch (M3)','iPad Air',2025,'ipad-301083.txt',S+'122242','iPad Air 13-in. (M3)',hig='iPad Air 13-inch',bio='touch-id',home=False,marketed=13),
 ip('ipad-air-11-inch-m3','iPad Air 11-inch (M3)','iPad Air',2025,'ipad-301081.txt',S+'122241','iPad Air 11-in. (M3)',hig='iPad Air 11-inch',bio='touch-id',home=False,marketed=11),
 ip('ipad-pro-13-inch-m4','iPad Pro 13-inch (M4)','iPad Pro',2024,'ipad-301033.txt',S+'119891','iPad Pro 13-in. (M4)',hig='iPad Pro 13-inch',bio='face-id',home=False,marketed=13),
 ip('ipad-pro-11-inch-m4','iPad Pro 11-inch (M4)','iPad Pro',2024,'ipad-301031.txt',S+'119892','iPad Pro 11-in. (M4)',hig='iPad Pro 11-inch 5th and 6th generation',bio='face-id',home=False,marketed=11),
 ip('ipad-air-13-inch-m2','iPad Air 13-inch (M2)','iPad Air',2024,'ipad-301029.txt',S+'119893','iPad Air 13-in. (M2)',hig='iPad Air 13-inch',bio='touch-id',home=False,marketed=13),
 ip('ipad-air-11-inch-m2','iPad Air 11-inch (M2)','iPad Air',2024,'ipad-301027.txt',S+'119894','iPad Air 11-in. (M2)',hig='iPad Air 11-inch',bio='touch-id',home=False,marketed=11),
 ip('ipad-mini-a17-pro','iPad mini (A17 Pro)','iPad mini',2024,'ipad-301063.txt',S+'121456','iPad Mini / (A17 Pro)',hig='iPad mini 8.3-inch',bio='touch-id',home=False,marketed=8.3),
 ip('ipad-10th-generation','iPad (10th generation)','iPad',2022,'ipad-300902.txt',S+'111840','iPad (10th generation)|iPad<br />{{Small|(10th generation)}}',same='iPad Air 10.9-inch',bio='touch-id',home=False,marketed=10.9),
 ip('ipad-air-5th-generation','iPad Air (5th generation)','iPad Air',2022,'ipad-300866.txt',S+'111887','iPad Air / (5th generation)',hig='iPad Air 10.9-inch',bio='touch-id',home=False),
 ip('ipad-pro-12-9-inch-6th-generation','iPad Pro 12.9-inch (6th generation)','iPad Pro',2022,'ipad-300908.txt',S+'111841','iPad Pro 12.9-in. / (6th generation)',hig='iPad Pro 12.9-inch',bio='face-id',home=False),
 ip('ipad-pro-11-inch-4th-generation','iPad Pro 11-inch (4th generation)','iPad Pro',2022,'ipad-300905.txt',S+'111842','iPad Pro 11-in. / (4th generation)',hig='iPad Pro 11-inch 1st–4th generation',bio='face-id',home=False),
 ip('ipad-9th-generation','iPad (9th generation)','iPad',2021,'ipad-300423.txt',S+'111898','iPad (9th generation)|iPad<br />{{Small|(9th generation)}}',hig='iPad 10.2-inch'),
 ip('ipad-mini-6th-generation','iPad mini (6th generation)','iPad mini',2021,'ipad-300425.txt',S+'111886','iPad Mini / (6th generation)',hig='iPad mini 8.3-inch',bio='touch-id',home=False,marketed=8.3),
 ip('ipad-pro-12-9-inch-5th-generation','iPad Pro 12.9-inch (5th generation)','iPad Pro',2021,'ipad-300349.txt',S+'111896','iPad Pro 12.9-in. / (5th generation)',hig='iPad Pro 12.9-inch',bio='face-id',home=False),
 ip('ipad-pro-11-inch-3rd-generation','iPad Pro 11-inch (3rd generation)','iPad Pro',2021,'ipad-300346.txt',S+'111897','iPad Pro 11-in. / (3rd generation)',hig='iPad Pro 11-inch 1st–4th generation',bio='face-id',home=False),
 ip('ipad-8th-generation','iPad (8th generation)','iPad',2020,'ipad-300200.txt',S+'118451','iPad (8th generation)|iPad<br />{{Small|(8th generation)}}',hig='iPad 10.2-inch'),
 ip('ipad-air-4th-generation','iPad Air (4th generation)','iPad Air',2020,'ipad-300202.txt',S+'111905','iPad Air / (4th generation)',hig='iPad Air 10.9-inch',bio='touch-id',home=False),
 ip('ipad-pro-12-9-inch-4th-generation','iPad Pro 12.9-inch (4th generation)','iPad Pro',2020,'ipad-509192.txt',S+'111977','iPad Pro 12.9-in. / (4th generation)',hig='iPad Pro 12.9-inch',bio='face-id',home=False),
 ip('ipad-pro-11-inch-2nd-generation','iPad Pro 11-inch (2nd generation)','iPad Pro',2020,'ipad-509181.txt',S+'118452','iPad Pro 11-in. / (2nd generation)',hig='iPad Pro 11-inch 1st–4th generation',bio='face-id',home=False),
 ip('ipad-7th-generation','iPad (7th generation)','iPad',2019,'ipad-507974.txt',S+'111911','iPad (7th generation)|iPad<br />{{Small|(7th generation)}}',hig='iPad 10.2-inch'),
 ip('ipad-air-3rd-generation','iPad Air (3rd generation)','iPad Air',2019,'ipad-506739.txt',S+'111939','iPad Air / (3rd generation)',hig='iPad Air 10.5-inch'),
 ip('ipad-mini-5th-generation','iPad mini (5th generation)','iPad mini',2019,'ipad-506704.txt',S+'111904','iPad mini / (5th generation)',hig='iPad mini 7.9-inch'),
 ip('ipad-pro-12-9-inch-3rd-generation','iPad Pro 12.9-inch (3rd generation)','iPad Pro',2018,'ipad-506047.txt',S+'111979','iPad Pro 12.9-in. / (3rd generation)',hig='iPad Pro 12.9-inch',bio='face-id',home=False),
 ip('ipad-pro-11-inch-1st-generation','iPad Pro 11-inch (1st generation)','iPad Pro',2018,'ipad-506083.txt',S+'111974','iPad Pro 11-in. / (1st generation)',hig='iPad Pro 11-inch 1st–4th generation',bio='face-id',home=False),
 ip('ipad-6th-generation','iPad (6th generation)','iPad',2018,'ipad-504852.txt',S+'111957','iPad (6th generation)|iPad<br />{{Small|(6th generation)}}',hig='iPad 9.7-inch'),
 ip('ipad-pro-12-9-inch-2nd-generation','iPad Pro 12.9-inch (2nd generation)','iPad Pro',2017,'ipad-503605.txt',S+'111964','iPad Pro 12.9-in. / (2nd generation)',hig='iPad Pro 12.9-inch'),
 ip('ipad-pro-10-5-inch','iPad Pro (10.5-inch)','iPad Pro',2017,'ipad-503642.txt',S+'111927','iPad Pro 10.5-in.',hig='iPad Pro 10.5-inch'),
 ip('ipad-5th-generation','iPad (5th generation)','iPad',2017,'ipad-503187.txt',S+'111960','iPad (5th generation)|iPad<br />{{Small|(5th generation)}}',hig='iPad 9.7-inch'),
 ip('ipad-pro-9-7-inch','iPad Pro (9.7-inch)','iPad Pro',2016,'ipad-501360.txt',S+'111965','iPad Pro 9.7-in.',hig='iPad Pro 9.7-inch'),
 ip('ipad-pro-12-9-inch-1st-generation','iPad Pro 12.9-inch (1st generation)','iPad Pro',2015,'ipad-500278.txt',S+'112024','iPad Pro 12.9-in. / (1st generation)',hig='iPad Pro 12.9-inch'),
 ip('ipad-mini-4','iPad mini 4','iPad mini',2015,'ipad-500106.txt',S+'112002','iPad mini 4',hig='iPad mini 7.9-inch'),
 ip('ipad-air-2','iPad Air 2','iPad Air',2014,'ipad-135088.txt',S+'112017','iPad Air 2',hig='iPad Air 9.7-inch'),
 ip('ipad-mini-3','iPad mini 3','iPad mini',2014,'ipad-135090.txt',S+'112018','iPad mini 3',hig='iPad mini 7.9-inch'),
 ip('ipad-air-1st-generation','iPad Air','iPad Air',2013,'ipad-134322.txt',S+'112020','iPad Air / (1st generation)',hig='iPad Air 9.7-inch',bio=None),
 ip('ipad-mini-2','iPad mini 2','iPad mini',2013,'ipad-134323.txt',S+'112019','iPad mini 2',hig='iPad mini 7.9-inch',bio=None),
 ip('ipad-4th-generation','iPad (4th generation)','iPad',2012,'ipad-133846.txt',S+'111993','iPad (4th generation)|iPad<br /><small>(4th generation)</small>',hig='iPad 9.7-inch',bio=None),
 ip('ipad-mini-1st-generation','iPad mini (1st generation)','iPad mini',2012,'ipad-133849.txt',S+'111978','iPad mini / (1st generation)',scale_rule=1,bio=None),
 ip('ipad-3rd-generation','iPad (3rd generation)','iPad',2012,'ipad-133608.txt',S+'111992','iPad (3rd generation)|iPad<br /><small>(3rd generation)</small>',hig='iPad 9.7-inch',bio=None),
 ip('ipad-2','iPad 2','iPad',2011,'ipad-133215.txt',S+'111990','iPad 2',scale_rule=1,bio=None),
 ip('ipad-1st-generation','iPad (1st generation)','iPad',2010,'ipad-132814.txt',S+'112438','iPad (1st generation)|iPad<br /><small>(1st generation)</small>',scale_rule=1,bio=None),
]

# ---------- iPod touch ----------
def ipod(id,name,year,spec,url,wiki,hig=None,same=None,scale_rule=None):
    return d(id,name,'ipod-touch','iPod touch',year,spec,url,wiki=wiki,hig=hig,hig_same_panel=same,scale_rule=scale_rule,cutout='none',biometric=None,home_button=True)
IPOD = [
 ipod('ipod-touch-7th-generation','iPod touch (7th generation)',2019,'ipod-507223.txt',S+'111961','iPod Touch (7th)',hig='iPod touch 5th generation and later'),
 ipod('ipod-touch-6th-generation','iPod touch (6th generation)',2015,'ipod-135428.txt',S+'112023','iPod Touch (6th)',hig='iPod touch 5th generation and later'),
 ipod('ipod-touch-5th-generation','iPod touch (5th generation)',2012,'ipod-133777.txt',S+'112021','iPod Touch (5th)',hig='iPod touch 5th generation and later'),
 ipod('ipod-touch-4th-generation','iPod touch (4th generation)',2010,'ipod-133019.txt',S+'112431','iPod Touch (4th)',scale_rule=2),
 ipod('ipod-touch-3rd-generation','iPod touch (3rd generation)',2009,'ipod-132670.txt',S+'112461','iPod Touch (3rd)',scale_rule=1),
 ipod('ipod-touch-2nd-generation','iPod touch (2nd generation)',2008,'ipod-132054.txt',S+'112319','iPod Touch (2nd)',scale_rule=1),
 ipod('ipod-touch-1st-generation','iPod touch (1st generation)',2007,'ipod-131660.txt',S+'112532','iPod Touch (1st)',scale_rule=1),
]

# ---------- Apple Watch ---------- one record per case size
# hig_watch = HIG watchOS table row ("Series" column) used for pixels when the Apple spec page omits them
def w(base,name,line,year,spec,url,sizes,hig_watch=None,year_src='apple'):
    out=[]
    for mm in sizes:
        out.append(d(f'{base}-{mm}mm',f'{name} {mm}mm','apple-watch',line,year,spec,url,case_mm=mm,hig_watch=hig_watch,cutout='none',biometric=None,home_button=False,year_source=year_src))
    return out
WATCH = (
  w('apple-watch-ultra-4','Apple Watch Ultra 4','Apple Watch Ultra',2026,'watch-sp148758.txt',S+'148758',[49],'Apple Watch Ultra (3rd generation)')
 +w('apple-watch-series-12','Apple Watch Series 12','Apple Watch Series',2026,'watch-sp148589.txt',S+'148589',[46,42],'10, 11')
 +w('apple-watch-ultra-3','Apple Watch Ultra 3','Apple Watch Ultra',2025,'watch-pl653.txt',S+'125095',[49],'Apple Watch Ultra (3rd generation)')
 +w('apple-watch-series-11','Apple Watch Series 11','Apple Watch Series',2025,'watch-sp125093.txt',S+'125093',[46,42],'10, 11')
 +w('apple-watch-se-3rd-generation','Apple Watch SE (3rd generation)','Apple Watch SE',2025,'watch-pl654.txt',S+'125094',[44,40],'4, 5, 6, and SE (all generations)')
 +w('apple-watch-series-10','Apple Watch Series 10','Apple Watch Series',2024,'watch-sp121202.txt',S+'121202',[46,42],'10, 11')
 +w('apple-watch-ultra-2','Apple Watch Ultra 2','Apple Watch Ultra',2023,'watch-301002.txt',S+'111832',[49],'Apple Watch Ultra (1st and 2nd generations)')
 +w('apple-watch-series-9','Apple Watch Series 9','Apple Watch Series',2023,'watch-sp111833.txt',S+'111833',[45,41],'7, 8, and 9')
 +w('apple-watch-ultra','Apple Watch Ultra','Apple Watch Ultra',2022,'watch-300895.txt',S+'111852',[49],'Apple Watch Ultra (1st and 2nd generations)')
 +w('apple-watch-series-8','Apple Watch Series 8','Apple Watch Series',2022,'watch-pl293.txt',S+'111848',[45,41],'7, 8, and 9')
 +w('apple-watch-se-2nd-generation','Apple Watch SE (2nd generation)','Apple Watch SE',2022,'watch-pl292.txt',S+'111853',[44,40],'4, 5, 6, and SE (all generations)')
 +w('apple-watch-series-7','Apple Watch Series 7','Apple Watch Series',2021,'watch-pl194.txt',S+'111909',[45,41],'7, 8, and 9')
 +w('apple-watch-se-1st-generation','Apple Watch SE (1st generation)','Apple Watch SE',2020,'watch-pl290.txt',S+'111862',[44,40],'4, 5, 6, and SE (all generations)')
 +w('apple-watch-series-6','Apple Watch Series 6','Apple Watch Series',2020,'watch-sp111918.txt',S+'111918',[44,40],'4, 5, 6, and SE (all generations)',year_src='wikipedia')
 +w('apple-watch-series-5','Apple Watch Series 5','Apple Watch Series',2019,'watch-sp118453.txt',S+'118453',[44,40],'4, 5, 6, and SE (all generations)',year_src='wikipedia')
 +w('apple-watch-series-4','Apple Watch Series 4','Apple Watch Series',2018,'watch-sp111984.txt',S+'111984',[44,40],'4, 5, 6, and SE (all generations)',year_src='wikipedia')
 +w('apple-watch-series-3','Apple Watch Series 3','Apple Watch Series',2017,'watch-sp111891.txt',S+'111891',[42,38],'1, 2, and 3',year_src='wikipedia')
 +w('apple-watch-series-2','Apple Watch Series 2','Apple Watch Series',2016,'watch-sp112022.txt',S+'112022',[42,38],'1, 2, and 3',year_src='wikipedia')
 +w('apple-watch-series-1','Apple Watch Series 1','Apple Watch Series',2016,'watch-sp111985.txt',S+'111985',[42,38],'1, 2, and 3',year_src='wikipedia')
 +w('apple-watch-1st-generation','Apple Watch (1st generation)','Apple Watch Series',2015,'watch-sp112009.txt',S+'112009',[42,38],None)
)

# ---------- Mac (partial: Apple silicon era + 2020 Intel models with built-in displays) ----------
def mac(id,name,line,year,spec,url):
    return d(id,name,'mac',line,year,spec,url,cutout=None,biometric='touch-id',home_button=False,partial=True)
MAC = [
 mac('macbook-pro-16-inch-m5-pro-max','MacBook Pro (16-inch, M5 Pro or M5 Max)','MacBook Pro',2026,'mac-301286.txt',S+'126319'),
 mac('macbook-pro-14-inch-m5-pro-max','MacBook Pro (14-inch, M5 Pro or M5 Max)','MacBook Pro',2026,'mac-301289.txt',S+'126318'),
 mac('macbook-air-15-inch-m5','MacBook Air (15-inch, M5)','MacBook Air',2026,'mac-301287.txt',S+'126321'),
 mac('macbook-air-13-inch-m5','MacBook Air (13-inch, M5)','MacBook Air',2026,'mac-301288.txt',S+'126320'),
 mac('macbook-neo','MacBook Neo','MacBook',2026,'mac-301292.txt',S+'126322'),
 mac('macbook-pro-14-inch-m5','MacBook Pro (14-inch, M5)','MacBook Pro',2025,'mac-301274.txt',S+'125405'),
 mac('macbook-air-15-inch-m4-2025','MacBook Air (15-inch, M4, 2025)','MacBook Air',2025,'mac-301087.txt',S+'122210'),
 mac('macbook-air-13-inch-m4-2025','MacBook Air (13-inch, M4, 2025)','MacBook Air',2025,'mac-301086.txt',S+'122209'),
 mac('macbook-pro-16-inch-2024','MacBook Pro (16-inch, 2024)','MacBook Pro',2024,'mac-301070.txt',S+'121554'),
 mac('macbook-pro-14-inch-m4-pro-max-2024','MacBook Pro (14-inch, M4 Pro or M4 Max, 2024)','MacBook Pro',2024,'mac-301069.txt',S+'121553'),
 mac('macbook-pro-14-inch-m4-2024','MacBook Pro (14-inch, M4, 2024)','MacBook Pro',2024,'mac-301068.txt',S+'121552'),
 mac('imac-24-inch-2024','iMac (24-inch, 2024)','iMac',2024,'mac-301066.txt',S+'121557'),
 mac('macbook-air-15-inch-m3-2024','MacBook Air (15-inch, M3, 2024)','MacBook Air',2024,'mac-301020.txt',S+'118552'),
 mac('macbook-air-13-inch-m3-2024','MacBook Air (13-inch, M3, 2024)','MacBook Air',2024,'mac-301019.txt',S+'118551'),
 mac('macbook-pro-16-inch-nov-2023','MacBook Pro (16-inch, Nov 2023)','MacBook Pro',2023,'mac-301012.txt',S+'117737'),
 mac('macbook-pro-14-inch-m3-pro-max-nov-2023','MacBook Pro (14-inch, M3 Pro or M3 Max, Nov 2023)','MacBook Pro',2023,'mac-301011.txt',S+'117736'),
 mac('macbook-pro-14-inch-m3-nov-2023','MacBook Pro (14-inch, M3, Nov 2023)','MacBook Pro',2023,'mac-301010.txt',S+'117735'),
 mac('imac-24-inch-m3-2023','iMac (24-inch, M3, 2023)','iMac',2023,'mac-301009.txt',S+'117734'),
 mac('macbook-air-15-inch-m2-2023','MacBook Air (15-inch, M2, 2023)','MacBook Air',2023,'mac-300954.txt',S+'111346'),
 mac('macbook-pro-16-inch-2023','MacBook Pro (16-inch, 2023)','MacBook Pro',2023,'mac-300926.txt',S+'111838'),
 mac('macbook-pro-14-inch-2023','MacBook Pro (14-inch, 2023)','MacBook Pro',2023,'mac-300925.txt',S+'111340'),
 mac('macbook-air-m2-2022','MacBook Air (M2, 2022)','MacBook Air',2022,'mac-300872.txt',S+'111867'),
 mac('macbook-pro-13-inch-m2-2022','MacBook Pro (13-inch, M2, 2022)','MacBook Pro',2022,'mac-300873.txt',S+'111869'),
 mac('macbook-pro-16-inch-2021','MacBook Pro (16-inch, 2021)','MacBook Pro',2021,'mac-300452.txt',S+'111901'),
 mac('macbook-pro-14-inch-2021','MacBook Pro (14-inch, 2021)','MacBook Pro',2021,'mac-300451.txt',S+'111902'),
 mac('imac-24-inch-m1-2021','iMac (24-inch, M1, 2021)','iMac',2021,'mac-300352.txt',S+'111895'),
 mac('macbook-air-m1-2020','MacBook Air (M1, 2020)','MacBook Air',2020,'mac-300267.txt',S+'111883'),
 mac('macbook-pro-13-inch-m1-2020','MacBook Pro (13-inch, M1, 2020)','MacBook Pro',2020,'mac-300266.txt',S+'111893'),
 mac('imac-retina-5k-27-inch-2020','iMac (Retina 5K, 27-inch, 2020)','iMac',2020,'mac-300198.txt',S+'111913'),
]

VISION = [
 d('apple-vision-pro-m5','Apple Vision Pro (M5)','vision','Apple Vision Pro',2025,'vision-sp125436.txt',S+'125436',cutout=None,biometric='optic-id',home_button=False,partial=True),
 d('apple-vision-pro','Apple Vision Pro','vision','Apple Vision Pro',2024,'vision-sp117810.txt',S+'117810',cutout=None,biometric='optic-id',home_button=False,partial=True),
]

ALL = IPHONE + IPAD + IPOD + WATCH + MAC + VISION
