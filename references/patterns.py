import re

patterns = {
    'ACL': re.compile(r'\b(association for computational linguistics|acl)\b', re.IGNORECASE),
    'AAAI': re.compile(r'\b(aaai|national conference on artificial intelligence)\b', re.IGNORECASE),
    'CIKM': re.compile(r'\b(conference on information and knowledge management|cikm)\b', re.IGNORECASE),
    'COLING': re.compile(r'\b(conference on computational linguistics|coling)\b', re.IGNORECASE),
    'CVPR': re.compile(r'\b(conference on computer vision and pattern recognition|cvpr)\b', re.IGNORECASE),
    'ECIR': re.compile(r'\b(european conference on information retrieval|ecir)\b', re.IGNORECASE),
    'EMNLP': re.compile(r'\b(empirical methods in natural language processing|emnlp)\b', re.IGNORECASE),
    'ICCV': re.compile(r'\b(international conference on computer vision|iccv)\b', re.IGNORECASE),
    'ICML': re.compile(r'\b(international conference on machine learning|icml)\b', re.IGNORECASE),
    'ICSE': re.compile(r'\b(international conference on software engineering|icse)\b', re.IGNORECASE),
    'IJCAI': re.compile(r'\b(international joint conference on artificial intelligence|ijcai)\b', re.IGNORECASE),
    'INFOCOM': re.compile(r'\b(international conference on computer communications|infocom)\b', re.IGNORECASE),
    'ISCA': re.compile(r'\b(international symposium on computer architecture|isca)\b', re.IGNORECASE),
    'KDD': re.compile(r'\b(knowledge discovery and data mining|kdd)\b', re.IGNORECASE),
    'MICRO': re.compile(r'\b(international symposium on microarchitecture|micro)\b', re.IGNORECASE),
    'MOBILECOMPUTING': re.compile(r'\b(international conference on mobile computing and networking|mobicom)\b', re.IGNORECASE),
    'NAACL': re.compile(r'\b(north american chapter of the association for computational linguistics|naacl)\b', re.IGNORECASE),
    'NIPS': re.compile(r'\b(advances in neural information processing systems|nips)\b', re.IGNORECASE),
    'PODC': re.compile(r'\b(principles of distributed computing|podc)\b', re.IGNORECASE),
    'SIGCOMM': re.compile(r'\b(special interest group on data communication|sigcomm)\b', re.IGNORECASE),
    'SIGGRAPH': re.compile(r'\b(SIG GRAPH|special interest group on computer graphics and interactive techniques|computer graphics and interactive techniques|siggraph)\b', re.IGNORECASE),
    'SIGIR': re.compile(r'\b(special interest group on information retrieval|sigir)\b', re.IGNORECASE),
    'SIGKDD': re.compile(r'\b(special interest group on knowledge discovery and data mining|sigkdd)\b', re.IGNORECASE),
    'SIGMETRICS': re.compile(r'\b(special interest group on performance evaluation|sigmetrics)\b', re.IGNORECASE),
    'SODA': re.compile(r'\b(symposium on discrete algorithms|soda)\b', re.IGNORECASE),
    'ACM Multimedia': re.compile(r'\b(acm multimedia|acm international conference on multimedia)\b', re.IGNORECASE),
    'CSCW': re.compile(r'\b(cscw|computer supported cooperative work and social computing)\b', re.IGNORECASE),
    'FSE': re.compile(r'\b(fse|acm sigsoft symposium on the foundations of software engineering)\b', re.IGNORECASE),
    'MOBICOM': re.compile(r'\b(mobicom|acm international conference on mobile computing and networking)\b', re.IGNORECASE),
    'NeurIPS': re.compile(r'\b(neurips|conference on neural information processing systems)\b', re.IGNORECASE),
    'OSDI': re.compile(r'\b(osdi|symposium on operating systems design and implementation)\b', re.IGNORECASE),
    'PLDI': re.compile(r'\b(pldi|acm sigplan conference on programming language design and implementation)\b', re.IGNORECASE),
    'POPL': re.compile(r'\b(popl|acm sigplan symposium on principles of programming languages)\b', re.IGNORECASE),
    'CCS': re.compile(r'\b(ACM CCS|Conference on Computer and Communications Security)\b', re.IGNORECASE),
    'MM': re.compile(r'\b(ACM Multimedia|International Conference on Multimedia)\b', re.IGNORECASE),
    'WSDM': re.compile(r'\b(ACM WSDM|Web Search and Data Mining)\b', re.IGNORECASE),
    'WWW': re.compile(r'\b(ACM WWW|International World Wide Web Conference)\b', re.IGNORECASE),
    'ECCV': re.compile(r'\b(ECCV|European Conference on Computer Vision)\b', re.IGNORECASE),
    'UAI': re.compile(r'\b(UAI|Conference on Uncertainty in Artificial Intelligence)\b', re.IGNORECASE),
    'COLT': re.compile(r'\b(COLT|Conference on Learning Theory)\b', re.IGNORECASE),
    'AISTATS': re.compile(r'\b(AISTATS|International Conference on Artificial Intelligence and Statistics)\b', re.IGNORECASE),
    'ICLR': re.compile(r'\b(ICLR|International Conference on Learning Representations)\b', re.IGNORECASE),
    'IJCNN': re.compile(r'\b(IJCNN|International Joint Conference on Neural Networks)\b', re.IGNORECASE),
    'ICANN': re.compile(r'\b(ICANN|International Conference on Artificial Neural Networks)\b', re.IGNORECASE),
    'ICPR': re.compile(r'\b(ICPR|International Conference on Pattern Recognition)\b', re.IGNORECASE),
    'UIST': re.compile(r'\b(ACM UIST|Conference on User Interface Software and Technology)\b', re.IGNORECASE),
    'ICRA': re.compile(r'\b(ICRA|IEEE International Conference on Robotics and Automation)\b', re.IGNORECASE),
    'IROS': re.compile(r'\b(IROS|IEEE/RSJ International Conference on Intelligent Robots and Systems)\b',re.IGNORECASE),
    'TRO': re.compile(r'\b(IEEE T-RO|Transactions on Robotics)\b', re.IGNORECASE),
    'PAMI': re.compile(r'\b(IEEE PAMI|Transactions on Pattern Analysis and Machine Intelligence)\b', re.IGNORECASE),
    'IJCV': re.compile(r'\b(IJCV|International Journal of Computer Vision)\b', re.IGNORECASE),
    'TPAMI': re.compile(r'\b(IEEE TPAMI|Transactions on Pattern Analysis and Machine Intelligence)\b', re.IGNORECASE),
    'JMLR': re.compile(r'\b(JMLR|Journal of Machine Learning Research)\b', re.IGNORECASE),
    'NeuroImage': re.compile(r'\b(NeuroImage|Journal of Brain Function)\b', re.IGNORECASE),
    'VL/HCC': re.compile(r'\b(VL/HCC|VL|HCC|IEEE Symposium on Visual Languages and Human-Centric Computing|Symposium on Visual Languages)\b', re.IGNORECASE),
    'ASPLOS': re.compile(r'\b(ASPLOS|ACM International Conference on Architectural Support for Programming Languages and Operating Systems)\b',re.IGNORECASE),
    'EuroSys': re.compile(r'\b(EuroSys|European Conference on Computer Systems)\b', re.IGNORECASE),
    'SOSP': re.compile(r'\b(SOSP|ACM Symposium on Operating Systems Principles)\b', re.IGNORECASE),
    'NSDI': re.compile(r'\b(NSDI|USENIX Symposium on Networked Systems Design and Implementation)\b', re.IGNORECASE),
    'TOIS': re.compile(r'\b(TOIS|ACM Transactions on Information Systems)\b', re.IGNORECASE),
    'TOIT': re.compile(r'\b(TOIT|ACM Transactions on Internet Technology)\b', re.IGNORECASE),
    'TOMCCAP': re.compile(r'\b(TOMCCAP|ACM Transactions on Multimedia Computing, Communications, and Applications)\b', re.IGNORECASE),
    #"VIS": re.compile(r"\b(VIS|IEEE VIS|IEEE Visualization)\b", re.IGNORECASE),
    "InfoVis": re.compile(r"\b(InfoVis|IEEE InfoVis| Information Visualization |IEEE Symposium on Information Visualization|VIS|IEEE VIS|IEEE Visualization)\b",re.IGNORECASE),
    "VAST": re.compile(r"\b(VAST|IEEE VAST|IEEE Visual Analytics Science and Technology)\b", re.IGNORECASE),
    "LDAV": re.compile(r"\b(LDAV|IEEE LDAV|IEEE Symposium on Large-Scale Data Analysis and Visualization)\b",re.IGNORECASE),
    "CHI": re.compile(r"\b(SIGCHI|BELIV|CHI|ACM CHI|ACM Conference on Human-Computer Interaction|Conference on Human Factors in Computing Systems)\b", re.IGNORECASE),
    "EuroVis": re.compile(r"\b(EuroVis|European Conference on Visualization)\b", re.IGNORECASE),
    "PacificVis": re.compile(r"\b(PacificVis|IEEE PacificVis|IEEE Pacific Visualization Symposium)\b",re.IGNORECASE),
    "IV": re.compile(r"\b(IV|IEEE IV| International Conference on Information Visualization | international conference information visualisation|IEEE Conference on Information Visualization Theory and Applications|International Conference on Information Visualisation)\b",re.IGNORECASE),
    'VINCI': re.compile(r'\b(Vinci|Visual Information Communication and Interaction)\b', re.IGNORECASE),
     #IEEE Transactions on Visualization and Computer Graphics
    #'IEEE TVCG': re.compile(r'\b(IEEE Transactions on Visualization and Computer Graphics|TVCG)\b', re.IGNORECASE),
    # ACM Transactions on Computer-Human Interaction (TOCHI)
    #'TOCHI': re.compile(r'\b(ACM Transactions on Computer-Human Interaction|TOCHI)\b', re.IGNORECASE),
    # Information Visualization Journal
    'Information Visualization': re.compile(r'\b(Information Visualization Journal|Information Visualization)\b', re.IGNORECASE),
    # Journal of Visualization
    'JOV': re.compile(r'\b(Journal of Visualization|JOV)\b', re.IGNORECASE),
    # Computer Graphics Forum
    'CGF': re.compile(r'\b(Computer Graphics Forum|CGF|Comput. Graph. Forum|comp. graph. forum)\b', re.IGNORECASE),
    # Journal of Computational and Graphical Statistics
    'JCGS': re.compile(r'\b(Journal of Computational and Graphical Statistics|JCGS)\b', re.IGNORECASE),
    # ACM Transactions on Interactive Intelligent Systems (TiiS)
    'TiiS': re.compile(r'\b(ACM Transactions on Interactive Intelligent Systems|TiiS)\b', re.IGNORECASE),
    # ACM Transactions on Intelligent Systems and Technology (TIST)
    'TIST': re.compile(r'\b(ACM Transactions on Intelligent Systems and Technology|TIST)\b', re.IGNORECASE),
    'SMC': re.compile(r'\b(Systems, Man, and Cybernetics|IEEE Transactions on Systems, Man, and Cybernetics: Systems|IEEE Trans. SMC: Systems)\b', re.IGNORECASE),
    'GD': re.compile(r'\b(GD|Graph Drawing)\b', re.IGNORECASE),
    'IUI': re.compile(r'\b(IUI|International Conference on Intelligent User Interfaces)\b', re.IGNORECASE),
    'CVGIP': re.compile(r'\b(CVGIP|Computer Vision, Graphics, and Image Processing)\b', re.IGNORECASE),
    'IEEE VR': re.compile(r'\b(VR|IEEE Virtual Reality Conference)\b', re.IGNORECASE),
    'IVCNZ': re.compile(r'\b(IVCNZ|International Conference on Image and Vision Computing New Zealand)\b',re.IGNORECASE),
    'GRAPP': re.compile(r'\b(GRAPP|International Conference on Computer Graphics Theory and Applications)\b',re.IGNORECASE),
    'Intelligent User Interfaces': re.compile(r'\b(Intelligent User Interfaces|International Conference on Intelligent User Interfaces)\b', re.IGNORECASE),
    'IEEE SMC Systems': re.compile(r'\b(IEEE Transactions on Systems, Man, and Cybernetics: Systems)\b', re.IGNORECASE),
    'TVCG': re.compile(r'\b(TVCG|Transaction on Computer Graphics|IEEE Transactions on Visualization and Computer Graphics|Visualization and Computer Graphics|IEEE\sTransactions\s?on\sComputer\s?Graphics\s?and\s?Visualization|ieee transactions on visualization & computer graphics)\b', re.IGNORECASE),
    'Journal of Visualization': re.compile(r'\b(Journal of Visualization)\b', re.IGNORECASE),
    'Computer Graphics Forum': re.compile(r'\b(Computer Graphics Forum)\b', re.IGNORECASE),
    'Journal of Computational and Graphical Statistics': re.compile( r'\b(Journal of Computational and Graphical Statistics)\b', re.IGNORECASE),
    'SG': re.compile(r'\b(SG|International Symposium on Smart Graphics|Smart Graphics)\b', re.IGNORECASE),
    'IEEE Automation Science and Engineering':re.compile(r'\bIEEE\s+Transactions\s+on\s+Automation\s+Science\s+and\s+Engineering\b', re.IGNORECASE),
    'TOCHI': re.compile(r'\b(ACM\sTransactions\s?on\s?Computer\s?-?\s?Human\s?Interaction)\b', re.IGNORECASE),
    #'TVCG': re.compile(r'\b(IEEE\sTransactions\s?on\sComputer\s?Graphics\s?and\s?Visualization)\b',re.IGNORECASE),
    'ISSG': re.compile(r'\b(International\s?Symposium\s?on\s?Smart\s?Graphics)\b', re.IGNORECASE),
    'IEEE TASE': re.compile(r'\b(IEEE\sTransactions\s?on\sAutomation\s?Science\s?and\s?Engineering)\b', re.IGNORECASE),
    'IEEE Systems': re.compile(r'\b(IEEE\sTransactions\s?on\s?Systems\s?,?\s?Man\s?,?\s?and\s?,?\s?Cybernetics\s?,?\s?Systems)\b',re.IGNORECASE),
    'IJHCS': re.compile(r'\b(International\s?Journal\s?of\s?Human-Computer\s?Studies)\b', re.IGNORECASE),
    "AutoSciEng": re.compile(r"\b(AutoSciEng&A|IEEE Transactions on Automation Science and Engineering)\b", re.IGNORECASE),
    #'Proceedings of Graphics Interface': re.compile(r'(Proceedings of Graphics Interface|Graphics Interface)', re.IGNORECASE),
    'CG&A': re.compile(r'\b(CG&A|Computer Graphics and Applications)\b', re.IGNORECASE),
    'TOG': re.compile(r'\b(TOG|ACM Transactions on Graphics|acm trans. graph)\b', re.IGNORECASE),
    'ISMAR': re.compile(r'\b(ISMAR|International Symposium on Mixed and Augmented Reality)\b', re.IGNORECASE),
    'ICIP': re.compile(r'\b(ICIP|IEEE International Conference on Image Processing)\b', re.IGNORECASE),
    'ITS': re.compile(r'\b(ITS|ACM Conference on Interactive Tabletops and Surfaces)\b', re.IGNORECASE),
    'GI': re.compile(r'\b(GI|Graphics Interface|Proceedings of Graphics Interface|Graphics Interface)\b', re.IGNORECASE),
    'WSCG': re.compile(r'\b(WSCG|International Conference on Computer Graphics, Visualization and Computer Vision)\b', re.IGNORECASE),
    'PCS': re.compile(r'\b(PCS|Pacific Conference on Computer Graphics and Applications)\b', re.IGNORECASE),
    'PG': re.compile(r'\b(PG|Practical Graphics)', re.IGNORECASE),
    'GRAPHITE': re.compile(r'GRAPHITE|International Conference on Computer Graphics and Interactive Techniques', re.IGNORECASE),
    'SMARTGRAPHICS': re.compile(r'SMARTGRAPHICS|International Symposium on Smart Graphics', re.IGNORECASE),
    'ISPG': re.compile(r'\b(ISPG|International Symposium on Smart Processing and Graphics)\b', re.IGNORECASE),
    'ISGG': re.compile(r'ISGG|International Symposium on Grids and Clouds', re.IGNORECASE),
    'ISGD': re.compile(r'ISGD|International Symposium on Smart Graphics and Development', re.IGNORECASE),
    'ISVC': re.compile(r'ISVC|International Symposium on Visual Computing', re.IGNORECASE),
    'ISGD&T': re.compile(r'ISGD&T|International Symposium on Smart Graphics, Data and Technology', re.IGNORECASE),
    'PGM':  re.compile(r'PGM|International Conference on Probabilistic Graphical Models', re.IGNORECASE),
    'ICVGIP': re.compile(r'ICVGIP|Indian Conference on Computer Vision, Graphics and Image Processing', re.IGNORECASE),
    'ICCP': re.compile(r'ICCP|IEEE International Conference on Computational Photography', re.IGNORECASE),
    'SUI': re.compile(r'SUI|Symposium on Spatial User Interaction', re.IGNORECASE),
    'GRAPH-HOC': re.compile(r'GRAPH-HOC|International Journal of Computer Graphics &amp; Animation', re.IGNORECASE),
    'WSCGJ': re.compile(r'WSCGJ|Journal of wscg|wscg', re.IGNORECASE),
    "Computational Physics Conference": re.compile(r"(computational physics conference|CPC)", re.IGNORECASE),
    'APGV': re.compile(r'\b(Applied Perception in Graphics and Visualization|apgv|ACM APGV)\b', re.IGNORECASE),
    'VISSOFT': re.compile(r'\b(IEEE International Workshop on Visualizing Software for Understanding and Analysis|VISSOFT|IEEE VISSOFT)\b', re.IGNORECASE),
    'CGA': re.compile(r'\b(IEEE Computer Graphics and Applications|IEEE CG&A|CG&A)\b', re.IGNORECASE),
    'LNCS': re.compile(r'\b(Lecture Notes in Computer Science|LNCS|Springer LNCS)\b', re.IGNORECASE),
    'WPC': re.compile(r'Workshop on Program Comprehension|WPC', re.IGNORECASE),
    'WCRE': re.compile(r'\b(Working Conference on Reverse Engineering|WCRE)\b', re.IGNORECASE),
    'ASE': re.compile(r'\b(ACM International Conference on Automated Software Engineering|ASE|ACM ASE)\b', re.IGNORECASE),
    'Web3D': re.compile(r'\b(International Conference on 3D Web Technology|Web3D|ACM Web3D)\b', re.IGNORECASE),
    'VISIGRAPP': re.compile(r'\b(International Joint Conference on Computer Vision, Imaging and Computer Graphics Theory and Applications|IVAPP|Proceedings of GRAPP/IVAPP)\b', re.IGNORECASE),
    'CRIWG': re.compile(r'\b(International Workshop on Groupware|CRIWG)\b', re.IGNORECASE),
    'ICPC': re.compile(r'\b(IEEE/ACM International Conference on Program Comprehension|ICPC)\b', re.IGNORECASE),
    'ISBI': re.compile(r'\b(International Symposium on Biomedical Imaging|ISBI)\b', re.IGNORECASE),
    'ISVC': re.compile(r'\b(International Symposium on Visual Computing|ISVC)\b', re.IGNORECASE),
    'CGVC': re.compile(r'\b(Computer Graphics & Visual Computing|CGVC)\b', re.IGNORECASE),
    'ICPP': re.compile(r'\b(International Conference on Parallel Processing|ICPP|Parallel Processing)\b', re.IGNORECASE),   
    'PLOS ONE': re.compile(r'\b(PLOS ONE|PloS one|inclusive journal community)\b', re.IGNORECASE),   
    'ISVC': re.compile(r'\b(International Symposium on Visual Computing|Advances in Visual Computing|ISVC)\b', re.IGNORECASE),   
    "Journal of Visual Languages & Computing": re.compile(r"(Journal of Visual Languages & Computing)", re.IGNORECASE),
    "Vision Research": re.compile(r"(Journal of Vision Research| Vision Research)", re.IGNORECASE),
    'UIST': re.compile(r'\b(ACM Symposium on User Interface Software and Technology|UIST|User Interface Software and Technology)\b', re.IGNORECASE),
    'DIS': re.compile(r'\b(ACM Conference on Designing Interactive Systems|DIS)\b', re.IGNORECASE),
    'CADCG': re.compile(r'\b(Journal of Computer-Aided Design & Computer Graphics|CAD)\b', re.IGNORECASE),
    'SIBGRAPI': re.compile(r'\b(Brazilian Symposium on Computer Graphics and Image Processing|SIBGRAPI)\b', re.IGNORECASE),
    'JVLC': re.compile(r'\b(Journal of Visual Languages and Computing|jvlc|Journal of Computer Languages)\b', re.IGNORECASE),
    'HICSS': re.compile(r'\b(Hawaii International Conference on System Sciences|HICSS)\b', re.IGNORECASE),
    'BIGDATA': re.compile(r'\b(International Conference on Big Data)\b', re.IGNORECASE),
    'IPMI': re.compile(r'\b(IPMI|International conference on information processing in medical imaging)\b', re.IGNORECASE),
    'EMBC': re.compile(r'\b(EMBC|Engineering in Medicine & Biology Society)\b', re.IGNORECASE),
    'JEP': re.compile(r'\b(jep|Journal of Experimental Psychology)\b', re.IGNORECASE),
    'AVR': re.compile(r'\b(AVR|International Conference on Augmented Reality)\b', re.IGNORECASE),
    'ISVD': re.compile(r'\b(ISVD|International Symposium on Voronoi Diagrams in Science and Engineering)\b', re.IGNORECASE),
    'DAM': re.compile(r'Discrete Applied Mathematics', re.IGNORECASE),
    'CSUR': re.compile(r'\b(acm computing surveys|surveys)\b', re.IGNORECASE),
    'SOCG': re.compile(r'symposium on computational geometry|SoCG', re.IGNORECASE),
    'jwtusm': re.compile(r'Journal of Wuhan Technical University of Surveying and Mapping', re.IGNORECASE),
    'ATSIP': re.compile(r'\b(International Conference on Advanced Technologies for Signal and Image Processing|ATSIP)\b', re.IGNORECASE),
    'jrss': re.compile(r'journal of the royal statistical society', re.IGNORECASE),
    'jcr': re.compile(r'journal of consumer research', re.IGNORECASE),
    'tvc': re.compile(r'the visual computer', re.IGNORECASE),
    'c&g': re.compile(r'\b(Computers and Graphics|computers & graphics|Journal of Systems & Applications in Computer Graphics)\b', re.IGNORECASE),
    'tas': re.compile(r'\b(the american statistician)\b', re.IGNORECASE),
    #'Science': re.compile(r'\bScience', re.IGNORECASE),
    'CoRR': re.compile(r'\b(CoRR|The Computing Research Repository|corr)\b', re.IGNORECASE),
    'jasist': re.compile(r'Journal of the American Society for Information Science', re.IGNORECASE),
    'comacm': re.compile(r'Communications of the ACM|Commun. ACM|communications of acm', re.IGNORECASE),
    'psychometrika': re.compile(r'Psychometrika', re.IGNORECASE),
    'jgaa': re.compile(r'Journal of Graph Algorithms and Applications', re.IGNORECASE),
    'euac': re.compile(r'Environment and Planning B: Urban Analytics and City Science|environment and planning b: planning and design', re.IGNORECASE),
    'dmkd': re.compile(r'data mining and knowledge discovery', re.IGNORECASE),
    'informationsciences': re.compile(r'\b(Information Sciences)', re.IGNORECASE),
    'jos': re.compile(r'\b(Journal of Software)', re.IGNORECASE),
    'Leonardo': re.compile(r'\b(Leonardo)', re.IGNORECASE),
    'tse': re.compile(r'\b(IEEE Transactions on Software Engineering)', re.IGNORECASE),
    'ieee software': re.compile(r'\b(ieee software| ieee)', re.IGNORECASE),
}

pub_patterns = {
    'sage': re.compile(r'SAGE Publications|Sage CA|Sage|sagepub', re.IGNORECASE),
    'plos one': re.compile(r'\b(plosone)\b', re.IGNORECASE),
    'ieee': re.compile(r'\b(ieee)\b', re.IGNORECASE),
    'acm': re.compile(r'ACM|acm|acmsiggraphb', re.IGNORECASE),
    'springer': re.compile(r'springer-verlag|springer|springeropen', re.IGNORECASE),
    'asa': re.compile(r'\b(american statistical association)\b', re.IGNORECASE),
    'elsevier': re.compile(r'Elsevier|Elsevier Science', re.IGNORECASE),
}