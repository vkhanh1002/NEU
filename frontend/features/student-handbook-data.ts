export interface HandbookGuide {
  id: string;
  stage: number;
  stageTitle: string;
  title: string;
  shortDesc: string;
  purpose: string;
  targetAudience: string;
  documentsNeeded: string[];
  steps: string[];
  locationOrUrl: string;
  processingTime?: string;
  importantNotes: string[];
  relatedLink?: {
    label: string;
    url: string;
  };
}

export interface NeuWebsite {
  id: string;
  name: string;
  shortName?: string;
  url: string;
  category: "daotao" | "thutuc" | "congnghe" | "thongtin" | "doisong";
  categoryLabel: string;
  description: string;
  features: string[];
  needs: string[]; // Mảng các tag nhu cầu, e.g. ["xem_lich_hoc", "tra_cuu_diem"]
  isVerified: boolean;
}

export interface StudentNeed {
  id: string;
  title: string;
  iconName: string;
  description: string;
  recommendedWebsiteId: string;
  usageGuide: string;
}

export const HANDBOOK_STAGES = [
  { id: 1, title: "Giai đoạn 1: Hoàn tất thủ tục nhập học", desc: "Xác nhận nhập học, chuẩn bị hồ sơ và nộp học phí ban đầu" },
  { id: 2, title: "Giai đoạn 2: Thiết lập tài khoản sinh viên", desc: "Kích hoạt email trường cấp, đăng nhập LMS, đổi mật khẩu" },
  { id: 3, title: "Giai đoạn 3: Hoàn thiện hồ sơ sinh viên", desc: "Cập nhật thông tin cá nhân, ảnh thẻ, giấy tờ trên cổng dữ liệu" },
  { id: 4, title: "Giai đoạn 4: Làm quen với chương trình học", desc: "Tìm hiểu quy chế tín chỉ, đăng ký môn học và tra cứu lịch thi" },
  { id: 5, title: "Giai đoạn 5: Sử dụng hệ thống học tập", desc: "Học tập trên LMS NEU, thư viện số Phạm Văn Đồng, tra cứu điểm" },
  { id: 6, title: "Giai đoạn 6: Khám phá đời sống sinh viên", desc: "Tham gia CLB, Đoàn - Hội, Ký túc xá và chính sách học bổng" },
];

export const HANDBOOK_GUIDES: HandbookGuide[] = [
  // Giai đoạn 1
  {
    id: "g1-xac-nhan-nhap-hoc",
    stage: 1,
    stageTitle: "Giai đoạn 1: Hoàn tất thủ tục nhập học",
    title: "1. Hướng dẫn xác nhận nhập học trực tuyến",
    shortDesc: "Xác nhận nguyện vọng trúng tuyển trên hệ thống Bộ GD&ĐT và Cổng tuyển sinh NEU.",
    purpose: "Khẳng định nguyện vọng học tập chính thức tại Trường Đại học Kinh tế Quốc dân để được cấp mã sinh viên.",
    targetAudience: "Tất cả thí sinh đã có thông báo trúng tuyển chính thức vào NEU.",
    documentsNeeded: [
      "Tài khoản và mật khẩu Cổng thông tin tuyển sinh của Bộ GD&ĐT",
      "Căn cước công dân gắn chip",
      "Giấy chứng nhận kết quả thi tốt nghiệp THPT (để nhập mã xác nhận)"
    ],
    steps: [
      "Bước 1: Đăng nhập vào hệ thống tuyển sinh chung của Bộ GD&ĐT (thisinh.thitotnghiepthpt.edu.vn).",
      "Bước 2: Tìm đến mục 'Tra cứu kết quả tuyển sinh' và chọn nguyện vọng trúng tuyển NEU.",
      "Bước 3: Nhấn nút 'Xác nhận nhập học' trước thời hạn Bộ quy định và in phiếu xác nhận.",
      "Bước 4: Truy cập Cổng tuyển sinh NEU (tuyensinh.neu.edu.vn) để khai báo hồ sơ nhập học đợt 1."
    ],
    locationOrUrl: "Cổng tuyển sinh Bộ GD&ĐT & tuyensinh.neu.edu.vn",
    processingTime: "Xử lý trực tuyến ngay lập tức",
    importantNotes: [
      "Thí sinh không xác nhận nhập học đúng hạn trên cổng Bộ GD&ĐT sẽ bị coi như từ chối cơ hội học tập.",
      "Chụp ảnh màn hình hoặc lưu mã xác nhận để đối chiếu khi cần."
    ],
    relatedLink: {
      label: "Cổng tuyển sinh NEU",
      url: "https://tuyensinh.neu.edu.vn"
    }
  },
  {
    id: "g1-chuan-bi-ho-so",
    stage: 1,
    stageTitle: "Giai đoạn 1: Hoàn tất thủ tục nhập học",
    title: "2. Chuẩn bị hồ sơ và giấy tờ nhập học bản cứng",
    shortDesc: "Các loại giấy tờ, công chứng cần nộp trực tiếp tại trường khi làm thủ tục.",
    purpose: "Hoàn thiện hồ sơ lưu trữ chính thức tại Phòng Công tác Chính trị & Quản lý sinh viên.",
    targetAudience: "Tân sinh viên khóa mới.",
    documentsNeeded: [
      "Bản chính Giấy chứng nhận kết quả thi tốt nghiệp THPT",
      "Bản sao công chứng Bằng tốt nghiệp THPT (hoặc Giấy chứng nhận tốt nghiệp tạm thời)",
      "Bản sao công chứng Học bạ THPT",
      "Bản sao Giấy khai sinh và Căn cước công dân (công chứng)",
      "04 ảnh 3x4 chụp trong vòng 6 tháng (ghi rõ họ tên, MSSV mặt sau)",
      "Hồ sơ chuyển sinh hoạt Đảng/Đoàn (nếu có), Giấy chuyển nghĩa vụ quân sự (đối với nam sinh viên)"
    ],
    steps: [
      "Bước 1: Soát lại toàn bộ danh mục giấy tờ theo Giấy báo trúng tuyển của NEU.",
      "Bước 2: Phân loại theo túi hồ sơ học sinh - sinh viên chuẩn.",
      "Bước 3: Nộp trực tiếp tại Hội trường A2 hoặc Nhà thi đấu NEU theo lịch hẹn từng khoa/ngành."
    ],
    locationOrUrl: "Hội trường A2 / Tòa nhà A1, Trường ĐH Kinh tế Quốc dân (207 Giải Phóng)",
    processingTime: "Theo khung giờ tiếp đón của từng khoa",
    importantNotes: [
      "Tất cả bản sao công chứng không quá 6 tháng.",
      "Bản chính Giấy chứng nhận kết quả thi THPT nộp sẽ không được trả lại, sinh viên nên sao lưu bản mềm trước."
    ]
  },
  {
    id: "g1-nop-hoc-phi",
    stage: 1,
    stageTitle: "Giai đoạn 1: Hoàn tất thủ tục nhập học",
    title: "3. Hướng dẫn nộp học phí nhập học ban đầu",
    shortDesc: "Cách thức chuyển khoản, số tài khoản chính thức của NEU và cú pháp chuyển tiền.",
    purpose: "Hoàn thành nghĩa vụ tài chính đầu khóa theo quy định đào tạo.",
    targetAudience: "Tân sinh viên và phụ huynh.",
    documentsNeeded: [
      "Mã hồ sơ xét tuyển hoặc Mã số sinh viên (MSSV) được cấp",
      "Ứng dụng Internet Banking hoặc thẻ ngân hàng"
    ],
    steps: [
      "Bước 1: Tra cứu mức học phí tạm thu học kỳ I trên thông báo nhập học.",
      "Bước 2: Thực hiện chuyển khoản vào tài khoản ngân hàng chính thức của Trường ĐH Kinh tế Quốc dân.",
      "Bước 3: Ghi đúng cú pháp chuyển khoản: [MSSV] - [Ho va Ten] - [Nop hoc phi nhap hoc].",
      "Bước 4: Kiểm tra trạng thái gạch nợ trên Cổng thông tin người học sau 1-2 ngày làm việc."
    ],
    locationOrUrl: "Cổng thông tin người học / Tài khoản Ngân hàng chính thức của NEU",
    processingTime: "1 - 2 ngày làm việc sau khi ngân hàng hạch toán",
    importantNotes: [
      "Chỉ nộp tiền vào đúng tài khoản thụ hưởng có tên 'TRUONG DAI HOC KINH TE QUOC DAN' tại các ngân hàng lớn (Vietcombank, BIDV, Agribank) công bố trên văn bản chính thức.",
      "Tuyệt đối không chuyển tiền vào tài khoản cá nhân của bất kỳ ai xưng là cán bộ trường."
    ]
  },

  // Giai đoạn 2
  {
    id: "g2-email-sinh-vien",
    stage: 2,
    stageTitle: "Giai đoạn 2: Thiết lập tài khoản sinh viên",
    title: "1. Kích hoạt và sử dụng Email sinh viên NEU",
    shortDesc: "Cấu trúc định dạng email Office 365, mật khẩu mặc định và cách kích hoạt bảo mật 2 lớp.",
    purpose: "Sử dụng email chính thức (@neu.edu.vn) để nhận thông báo học vụ, lịch thi và liên hệ giảng viên.",
    targetAudience: "Tân sinh viên đã được cấp mã số sinh viên.",
    documentsNeeded: [
      "Mã số sinh viên (MSSV)",
      "Số CCCD đăng ký khi nhập học"
    ],
    steps: [
      "Bước 1: Truy cập outlook.office.com hoặc mail.neu.edu.vn.",
      "Bước 2: Nhập địa chỉ email sinh viên theo định dạng: [MSSV]@neu.edu.vn (Ví dụ: 11240001@neu.edu.vn).",
      "Bước 3: Nhập mật khẩu khởi tạo được cấp trong giấy báo hoặc định dạng Neu@[ngay_thang_nam_sinh].",
      "Bước 4: Thiết lập mật khẩu mới phức tạp và kích hoạt xác thực 2 lớp qua Microsoft Authenticator."
    ],
    locationOrUrl: "https://mail.neu.edu.vn hoặc outlook.office.com",
    processingTime: "Kích hoạt tức thì",
    importantNotes: [
      "Tài khoản Office 365 của trường cho phép cài đặt miễn phí bộ Office Word/Excel/PowerPoint bản quyền trên 5 thiết bị.",
      "Mọi thông báo thi cử, học bổng chỉ được gửi vào email này."
    ],
    relatedLink: {
      label: "Truy cập Email NEU",
      url: "https://mail.neu.edu.vn"
    }
  },
  {
    id: "g2-doi-mat-khau",
    stage: 2,
    stageTitle: "Giai đoạn 2: Thiết lập tài khoản sinh viên",
    title: "2. Hướng dẫn đổi và khôi phục mật khẩu tài khoản học tập",
    shortDesc: "Cách đổi mật khẩu cổng thông tin người học, portal tín chỉ và các hệ sinh thái NEU.",
    purpose: "Bảo đảm an toàn thông tin cá nhân và tài khoản đăng ký môn học.",
    targetAudience: "Toàn bộ sinh viên NEU.",
    documentsNeeded: [
      "Tài khoản email trường đã kích hoạt",
      "Số điện thoại sinh viên đã đăng ký"
    ],
    steps: [
      "Bước 1: Truy cập password.neu.edu.vn hoặc mục 'Đổi mật khẩu' trên Cổng thông tin người học.",
      "Bước 2: Nhập tên đăng nhập (MSSV) và mã kiểm tra.",
      "Bước 3: Xác thực qua mã OTP gửi về email sinh viên hoặc số điện thoại.",
      "Bước 4: Nhập mật khẩu mới gồm ít nhất 8 ký tự, có chữ hoa, chữ thường và số."
    ],
    locationOrUrl: "https://password.neu.edu.vn hoặc Phòng 301 Nhà A1 (Trung tâm Ứng dụng CNTT)",
    processingTime: "Tự động 24/7",
    importantNotes: [
      "Không chia sẻ tài khoản cho bạn bè trong đợt đăng ký tín chỉ để tránh bị hủy môn hoặc lộ dữ liệu."
    ]
  },

  // Giai đoạn 3
  {
    id: "g3-hoan-thien-ho-so",
    stage: 3,
    stageTitle: "Giai đoạn 3: Hoàn thiện hồ sơ sinh viên",
    title: "1. Cập nhật hồ sơ sinh viên trên Cổng dữ liệu trực tuyến",
    shortDesc: "Bổ sung ảnh thẻ làm thẻ sinh viên ngân hàng, thông tin cư trú và người liên hệ khẩn cấp.",
    purpose: "Đồng bộ cơ sở dữ liệu quốc gia về giáo dục và phát hành thẻ sinh viên tích hợp thẻ ngân hàng.",
    targetAudience: "Tân sinh viên trong tháng đầu tiên nhập học.",
    documentsNeeded: [
      "File ảnh thẻ 3x4 phông nền xanh hoặc trắng (chuẩn định dạng .jpg/.png)",
      "Thông tin địa chỉ tạm trú tại Hà Nội",
      "Số CCCD của phụ huynh (cha/mẹ/người giám hộ)"
    ],
    steps: [
      "Bước 1: Đăng nhập vào Cổng dữ liệu sinh viên (dulieusinhvien.neu.edu.vn).",
      "Bước 2: Vào mục 'Thông tin cá nhân' -> Rà soát lại họ tên, ngày sinh, quê quán.",
      "Bước 3: Tải ảnh thẻ chất lượng cao (rõ mặt, nghiêm túc) để in phôi thẻ sinh viên.",
      "Bước 4: Điền thông tin địa chỉ cư trú hiện tại và thông tin liên hệ khẩn cấp, sau đó nhấn 'Lưu hồ sơ'."
    ],
    locationOrUrl: "https://dulieusinhvien.neu.edu.vn",
    processingTime: "Thực hiện trước hạn chót tuần thứ 4 của học kỳ I",
    importantNotes: [
      "Ảnh thẻ sau khi duyệt sẽ không thể tự thay đổi vì được dùng in Thẻ sinh viên và bằng tốt nghiệp sau này."
    ],
    relatedLink: {
      label: "Cổng dữ liệu sinh viên NEU",
      url: "https://dulieusinhvien.neu.edu.vn"
    }
  },

  // Giai đoạn 4
  {
    id: "g4-dang-ky-tin-chi",
    stage: 4,
    stageTitle: "Giai đoạn 4: Làm quen với chương trình học",
    title: "1. Hướng dẫn quy chế tín chỉ và đăng ký học phần",
    shortDesc: "Cách xem cây chương trình đào tạo, điều kiện tiên quyết và cách bấm lớp tín chỉ.",
    purpose: "Chủ động xây dựng kế hoạch học tập theo tiến độ cá nhân (3 năm, 3.5 năm hoặc 4 năm).",
    targetAudience: "Sinh viên các khóa đang theo học tại trường.",
    documentsNeeded: [
      "Khung chương trình đào tạo ngành học của khóa mình",
      "Thời khóa biểu dự kiến do Phòng Quản lý Đào tạo công bố"
    ],
    steps: [
      "Bước 1: Tân sinh viên học kỳ I thường được Nhà trường xếp lịch sẵn theo lớp sinh viên.",
      "Bước 2: Từ học kỳ II, truy cập tinchi.neu.edu.vn theo khung giờ đăng ký của khóa mình.",
      "Bước 3: Lựa chọn học phần, chọn lớp học phần phù hợp với thời khóa biểu.",
      "Bước 4: Nhấn 'Lưu đăng ký' và kiểm tra lại danh sách môn học đã chọn trong mục 'Kết quả đăng ký'."
    ],
    locationOrUrl: "https://tinchi.neu.edu.vn và daotao.neu.edu.vn",
    processingTime: "Mở theo các đợt đăng ký đầu học kỳ",
    importantNotes: [
      "Chú ý các môn học có học phần tiên quyết (phải qua môn A mới được học môn B).",
      "Số tín chỉ đăng ký tối thiểu là 14 tín chỉ/kỳ chính, tối đa 25 tín chỉ/kỳ."
    ],
    relatedLink: {
      label: "Cổng đăng ký tín chỉ",
      url: "https://tinchi.neu.edu.vn"
    }
  },

  // Giai đoạn 5
  {
    id: "g5-su-dung-lms",
    stage: 5,
    stageTitle: "Giai đoạn 5: Sử dụng hệ thống học tập",
    title: "1. Hướng dẫn học tập và nộp bài trên LMS NEU",
    shortDesc: "Vào lớp học trực tuyến, tải bài giảng tài liệu và nộp assignment đúng deadline.",
    purpose: "Tham gia các hoạt động học tập kết hợp (Blended Learning) theo từng môn học.",
    targetAudience: "Toàn bộ sinh viên NEU.",
    documentsNeeded: [
      "Tài khoản Office 365 sinh viên",
      "Mã lớp học phần do giảng viên cung cấp (nếu có)"
    ],
    steps: [
      "Bước 1: Truy cập lms.neu.edu.vn hoặc courses.neu.edu.vn.",
      "Bước 2: Đăng nhập bằng nút 'Đăng nhập với tài khoản NEU Office 365'.",
      "Bước 3: Chọn khóa học trong danh sách 'Các khóa học của tôi'.",
      "Bước 4: Tải slide bài giảng, tham gia diễn đàn trao đổi và nộp bài tập đúng hạn."
    ],
    locationOrUrl: "https://lms.neu.edu.vn",
    processingTime: "Truy cập liên tục trong suốt học kỳ",
    importantNotes: [
      "Hệ thống sẽ đóng tự động khi hết hạn nộp bài tập (deadline). Hãy luôn nộp trước ít nhất 1-2 tiếng để tránh nghẽn mạng."
    ],
    relatedLink: {
      label: "Hệ thống LMS NEU",
      url: "https://lms.neu.edu.vn"
    }
  },
  {
    id: "g5-thu-vien-pham-van-dong",
    stage: 5,
    stageTitle: "Giai đoạn 5: Sử dụng hệ thống học tập",
    title: "2. Hướng dẫn sử dụng Thư viện Phạm Văn Đồng & Thư viện số",
    shortDesc: "Mượn giáo trình, sử dụng phòng tự học, máy tính tra cứu và cơ sở dữ liệu số.",
    purpose: "Tiếp cận kho tài liệu học tập, giáo trình chuẩn và không gian học tập hiện đại bậc nhất.",
    targetAudience: "Sinh viên và giảng viên NEU.",
    documentsNeeded: [
      "Thẻ sinh viên NEU (hoặc ứng dụng sinh viên có mã vạch barcode)"
    ],
    steps: [
      "Bước 1: Quét mã thẻ sinh viên tại cổng kiểm soát ra vào Thư viện Phạm Văn Đồng (Tòa nhà cạnh Nhà A1).",
      "Bước 2: Để ba lô túi xách vào tủ gửi đồ tự động tại tầng 1.",
      "Bước 3: Sử dụng các tầng chuyên biệt: Tầng 2 (sách mượn về), Tầng 3 (sách đọc tại chỗ & phòng học nhóm), Tầng 4 (tài liệu ngoại văn & cơ sở dữ liệu điện tử).",
      "Bước 4: Tra cứu tài liệu số trực tuyến tại neulib.neu.edu.vn hoặc reader.neu.edu.vn."
    ],
    locationOrUrl: "Tòa nhà Thư viện Phạm Văn Đồng, Trường ĐH Kinh tế Quốc dân",
    processingTime: "Mở cửa từ 07:30 - 21:00 (Thứ 2 - Thứ 7)",
    importantNotes: [
      "Giữ gìn trật tự và giữ vệ sinh chung, không mang đồ ăn có mùi vào phòng đọc.",
      "Sách mượn về cần gia hạn đúng hạn trên website thư viện để tránh bị phạt khóa thẻ."
    ],
    relatedLink: {
      label: "Cổng thông tin Thư viện NEU",
      url: "https://neulib.neu.edu.vn"
    }
  },

  // Giai đoạn 6
  {
    id: "g6-clb-doan-hoi",
    stage: 6,
    stageTitle: "Giai đoạn 6: Khám phá đời sống sinh viên",
    title: "1. Khám phá các CLB, Đội, Nhóm và Phong trào Đoàn - Hội",
    shortDesc: "Hơn 50 CLB chuyên môn, sở thích, tình nguyện và cách đăng ký phỏng vấn mùa Gen mới.",
    purpose: "Phát triển kỹ năng mềm, mở rộng mối quan hệ và tích lũy điểm rèn luyện.",
    targetAudience: "Tân sinh viên yêu thích hoạt động ngoại khóa.",
    documentsNeeded: [
      "CV cá nhân hoặc đơn đăng ký tham gia (theo form từng CLB phát động)"
    ],
    steps: [
      "Bước 1: Theo dõi ngày hội 'Chào tân sinh viên' hoặc 'Ngày hội các Câu lạc bộ (Club Day)' tại Sân ký túc xá / Sân nhà A1 vào tháng 9 - tháng 10.",
      "Bước 2: Tìm hiểu các nhóm CLB: Học thuật (Kinh tế, Chứng khoán, Marketing...), Sở thích (Âm nhạc MEC, Nhảy, Nhiếp ảnh...), Kỹ năng & Tình nguyện (Đội SVTN đồng hương, Đội Lễ tân...).",
      "Bước 3: Đăng ký ứng tuyển đợt tuyển thành viên (Gen mới) và tham gia các vòng phỏng vấn/thử thách.",
      "Bước 4: Tích lũy giấy chứng nhận hoạt động để nộp xét Điểm rèn luyện hàng kỳ."
    ],
    locationOrUrl: "Trang Đoàn Thanh niên (youth.neu.edu.vn) & Hội Sinh viên NEU",
    processingTime: "Mùa tuyển quân rầm rộ nhất vào tháng 9 - 11 hàng năm",
    importantNotes: [
      "Nên chọn 1-2 CLB phù hợp nhất với năng lực và thời gian biểu để không ảnh hưởng đến kết quả học tập trên lớp."
    ],
    relatedLink: {
      label: "Đoàn Thanh niên NEU",
      url: "https://youth.neu.edu.vn"
    }
  },
  {
    id: "g6-ky-tuc-xa",
    stage: 6,
    stageTitle: "Giai đoạn 6: Khám phá đời sống sinh viên",
    title: "2. Đăng ký lưu trú Ký túc xá và Dịch vụ sinh viên",
    shortDesc: "Điều kiện xét ở KTX, thủ tục đăng ký phòng và các dịch vụ tiện ích nội khu.",
    purpose: "Hỗ trợ chỗ ở an toàn, thuận tiện ngay trong khuôn viên trường cho sinh viên ở xa.",
    targetAudience: "Tân sinh viên thuộc diện chính sách, ưu tiên hoặc sinh viên ở các tỉnh xa.",
    documentsNeeded: [
      "Đơn đăng ký ở KTX theo mẫu của Ban Quản lý",
      "Giấy tờ chứng minh đối tượng ưu tiên (con thương binh, hộ nghèo, vùng sâu vùng xa - nếu có)",
      "Bản sao CCCD và Giấy báo trúng tuyển"
    ],
    steps: [
      "Bước 1: Nộp đơn đăng ký trực tuyến theo thông báo tuyển sinh hoặc nộp trực tiếp tại Văn phòng Ban Quản lý KTX.",
      "Bước 2: Theo dõi danh sách được duyệt bố trí phòng ở trên website trường.",
      "Bước 3: Nhận phòng, ký cam kết nội quy và hoàn tất nộp tiền lệ phí phòng ở.",
      "Bước 4: Làm thẻ ra vào KTX và đăng ký tạm trú theo hướng dẫn của quản lý tòa nhà."
    ],
    locationOrUrl: "Khu nội trú Ký túc xá NEU, Cổng Trần Đại Nghĩa",
    processingTime: "Theo đợt xét tiếp nhận đầu năm học",
    importantNotes: [
      "KTX NEU có phòng khép kín điều hòa, wifi, căn tin, sân bóng rổ và bảo vệ 24/7.",
      "Tuân thủ nghiêm ngặt quy định giờ giới nghiêm và an toàn phòng chống cháy nổ."
    ]
  }
];

export const NEU_WEBSITES: NeuWebsite[] = [
  // Nhóm 1: Đào tạo và học tập
  {
    id: "nguoihoc-neu",
    name: "Cổng thông tin người học",
    shortName: "Người học NEU",
    url: "https://nguoihoc.neu.edu.vn",
    category: "daotao",
    categoryLabel: "Đào tạo & Học tập",
    description: "Cổng tra cứu tổng thể: Thời khóa biểu, lịch thi, bảng điểm học tập, công nợ học phí và đánh giá rèn luyện.",
    features: ["Lịch học", "Lịch thi", "Tra cứu điểm", "Học phí", "Đánh giá điểm rèn luyện"],
    needs: ["xem_lich_hoc", "xem_lich_thi", "tra_cuu_diem", "kiem_tra_hoc_phi"],
    isVerified: true
  },
  {
    id: "daotao-neu",
    name: "Phòng Quản lý Đào tạo",
    shortName: "QLĐT NEU",
    url: "https://daotao.neu.edu.vn",
    category: "daotao",
    categoryLabel: "Đào tạo & Học tập",
    description: "Kênh thông báo học vụ chính thức: kế hoạch năm học, lịch thi lại, danh sách tốt nghiệp, quy chế đào tạo.",
    features: ["Thông báo đào tạo", "Lịch học vụ chung", "Biểu mẫu học vụ", "Quy chế đào tạo"],
    needs: ["xem_chuong_trinh_dao_tao", "tim_kiem_thong_bao"],
    isVerified: true
  },
  {
    id: "tinchi-neu",
    name: "Hệ thống đăng ký tín chỉ",
    shortName: "Tín chỉ NEU",
    url: "https://tinchi.neu.edu.vn",
    category: "daotao",
    categoryLabel: "Đào tạo & Học tập",
    description: "Hệ thống đăng ký môn học trực tuyến theo kỳ, chọn lớp học phần, hủy học phần và kiểm tra lịch trùng.",
    features: ["Đăng ký môn học", "Rút học phần", "Thời khóa biểu cá nhân"],
    needs: ["dang_ky_tin_chi", "xem_lich_hoc"],
    isVerified: true
  },
  {
    id: "lms-neu",
    name: "Hệ thống học tập trực tuyến LMS",
    shortName: "LMS NEU",
    url: "https://lms.neu.edu.vn",
    category: "daotao",
    categoryLabel: "Đào tạo & Học tập",
    description: "Nền tảng nộp bài tập assignment, tải slide bài giảng của giảng viên, làm bài quiz và tham gia lớp học số.",
    features: ["Tải bài giảng", "Nộp assignment", "Kiểm tra trắc nghiệm", "Diễn đàn môn học"],
    needs: ["tim_tai_lieu_hoc_tap"],
    isVerified: true
  },
  {
    id: "courses-neu",
    name: "Khóa học trực tuyến Courses NEU",
    shortName: "Courses NEU",
    url: "https://courses.neu.edu.vn",
    category: "daotao",
    categoryLabel: "Đào tạo & Học tập",
    description: "Hệ thống bổ trợ học tập E-Learning và bài giảng tương tác đa phương tiện của trường.",
    features: ["E-Learning", "Video bài giảng", "Khoá học chuyên ngành"],
    needs: ["tim_tai_lieu_hoc_tap"],
    isVerified: true
  },
  {
    id: "neulib-neu",
    name: "Cổng thông tin Thư viện Phạm Văn Đồng",
    shortName: "Thư viện NEU",
    url: "https://neulib.neu.edu.vn",
    category: "daotao",
    categoryLabel: "Đào tạo & Học tập",
    description: "Tra cứu mục lục sách, giáo trình, luận văn thạc sĩ/tiến sĩ, gia hạn mượn sách trực tuyến.",
    features: ["Tra cứu giáo trình", "Gia hạn sách", "Đặt phòng học nhóm", "Cơ sở dữ liệu khoa học"],
    needs: ["tim_tai_lieu_hoc_tap"],
    isVerified: true
  },
  {
    id: "reader-neu",
    name: "NEU Reader – Thư viện tài liệu số",
    shortName: "NEU Reader",
    url: "https://reader.neu.edu.vn",
    category: "daotao",
    categoryLabel: "Đào tạo & Học tập",
    description: "Đọc sách điện tử, bài báo khoa học và tạp chí Kinh tế & Phát triển bản quyền của NEU.",
    features: ["Đọc sách điện tử", "Tạp chí NEU", "Sách chuyên khảo"],
    needs: ["tim_tai_lieu_hoc_tap"],
    isVerified: true
  },

  // Nhóm 2: Thủ tục và công tác sinh viên
  {
    id: "onegate-neu",
    name: "Hệ thống Dịch vụ Một cửa NEU",
    shortName: "Một cửa NEU",
    url: "https://onegate.neu.edu.vn",
    category: "thutuc",
    categoryLabel: "Thủ tục & QLSV",
    description: "Tiếp nhận và giải quyết thủ tục hành chính trực tuyến: cấp giấy xác nhận sinh viên, bảng điểm, đơn từ học vụ.",
    features: ["Giấy xác nhận SV", "Bảng điểm xác nhận", "Hoãn nghĩa vụ quân sự", "Vay vốn chính sách"],
    needs: ["xin_giay_xac_nhan_sv"],
    isVerified: true
  },
  {
    id: "dulieusinhvien-neu",
    name: "Cổng dữ liệu sinh viên NEU",
    shortName: "Dữ liệu sinh viên",
    url: "https://dulieusinhvien.neu.edu.vn",
    category: "thutuc",
    categoryLabel: "Thủ tục & QLSV",
    description: "Cập nhật lý lịch cá nhân, tải ảnh thẻ sinh viên, khai báo BHYT và tra cứu thông tin hồ sơ gốc.",
    features: ["Khai báo hồ sơ", "Ảnh thẻ", "Bảo hiểm y tế", "Hồ sơ đoàn viên"],
    needs: ["xin_giay_xac_nhan_sv"],
    isVerified: true
  },
  {
    id: "phongctctqlsv-neu",
    name: "Phòng Công tác Chính trị & Quản lý sinh viên",
    shortName: "CTCT & QLSV",
    url: "https://phongctctqlsv.neu.edu.vn",
    category: "thutuc",
    categoryLabel: "Thủ tục & QLSV",
    description: "Thông tin chế độ chính sách, học bổng khuyến khích, khen thưởng, kỷ luật và các phong trào sinh viên.",
    features: ["Học bổng tài trợ", "Miễn giảm học phí", "Đánh giá rèn luyện", "Khen thưởng kỷ luật"],
    needs: ["tim_kiem_thong_bao"],
    isVerified: true
  },
  {
    id: "youth-neu",
    name: "Đoàn Thanh niên Trường ĐH Kinh tế Quốc dân",
    shortName: "Đoàn Thanh niên",
    url: "https://youth.neu.edu.vn",
    category: "thutuc",
    categoryLabel: "Thủ tục & QLSV",
    description: "Hoạt động Đoàn, mùa hè xanh, hiến máu nhân đạo, xét chọn sinh viên tiêu biểu và phong trào tình nguyện.",
    features: ["Sinh hoạt Đoàn", "Chiến dịch tình nguyện", "Giải thưởng Sao Tháng Giêng"],
    needs: ["tim_kiem_thong_bao"],
    isVerified: true
  },

  // Nhóm 3: Tài khoản và công nghệ
  {
    id: "mail-neu",
    name: "Hệ thống Email sinh viên NEU Office 365",
    shortName: "Email NEU",
    url: "https://mail.neu.edu.vn",
    category: "congnghe",
    categoryLabel: "Tài khoản & Công nghệ",
    description: "Hòm thư điện tử chính thức (@neu.edu.vn) cấp miễn phí cho toàn bộ sinh viên trong suốt khóa học.",
    features: ["Hộp thư Outlook", "Lưu trữ OneDrive 1TB", "Office 365 miễn phí", "Teams"],
    needs: ["tim_kiem_thong_bao"],
    isVerified: true
  },
  {
    id: "password-neu",
    name: "Cổng quản lý và khôi phục mật khẩu NEU",
    shortName: "Password NEU",
    url: "https://password.neu.edu.vn",
    category: "congnghe",
    categoryLabel: "Tài khoản & Công nghệ",
    description: "Đổi mật khẩu tài khoản hệ sinh thái số NEU và khôi phục mật khẩu tự động qua OTP.",
    features: ["Đổi mật khẩu", "Quên mật khẩu", "Kích hoạt tài khoản"],
    needs: [],
    isVerified: true
  },
  {
    id: "cait-neu",
    name: "Trung tâm Ứng dụng CNTT (CAIT)",
    shortName: "Trung tâm CNTT",
    url: "https://cait.neu.edu.vn",
    category: "congnghe",
    categoryLabel: "Tài khoản & Công nghệ",
    description: "Hỗ trợ kỹ thuật mạng wifi NEU-Campus, bảo trì hạ tầng công nghệ và tiếp nhận lỗi kỹ thuật cổng thông tin.",
    features: ["Hỗ trợ kỹ thuật", "Wifi trường", "Cấp lại tài khoản", "Bảo mật thông tin"],
    needs: ["tim_kiem_thong_bao"],
    isVerified: true
  },

  // Nhóm 4: Thông tin và phát triển bản thân
  {
    id: "neu-edu-vn",
    name: "Cổng thông tin điện tử chính thức ĐH Kinh tế Quốc dân",
    shortName: "Website NEU",
    url: "https://neu.edu.vn",
    category: "thongtin",
    categoryLabel: "Thông tin & Phát triển",
    description: "Trang tin tức trung tâm của trường: tin sự kiện, thông báo điều hành, hợp tác quốc tế và giới thiệu các khoa/viện.",
    features: ["Tin tức trường", "Sự kiện nổi bật", "Thông báo chung", "Cơ cấu tổ chức"],
    needs: ["tim_kiem_thong_bao", "xem_chuong_trinh_dao_tao"],
    isVerified: true
  },
  {
    id: "jobs-neu",
    name: "Cổng Thông tin Hướng nghiệp & Việc làm NEU",
    shortName: "NEU Career / Jobs",
    url: "https://jobs.neu.edu.vn",
    category: "thongtin",
    categoryLabel: "Thông tin & Phát triển",
    description: "Kết nối sinh viên với các tập đoàn lớn, thông báo ngày hội việc làm (Job Fair) và cơ hội thực tập có lương.",
    features: ["Tuyển dụng thực tập", "Việc làm doanh nghiệp", "Ngày hội tuyển dụng", "Hội thảo kỹ năng CV"],
    needs: ["tim_kiem_viec_lam"],
    isVerified: true
  },
  {
    id: "aep-neu",
    name: "Trung tâm Đào tạo Tiên tiến, CLC & POHE (AEP)",
    shortName: "AEP NEU",
    url: "https://aep.neu.edu.vn",
    category: "thongtin",
    categoryLabel: "Thông tin & Phát triển",
    description: "Trang chuyên trách dành riêng cho sinh viên các chương trình Tiên tiến, Chất lượng cao và POHE.",
    features: ["Lịch học AEP", "Học bổng AEP", "Trao đổi quốc tế"],
    needs: ["xem_chuong_trinh_dao_tao"],
    isVerified: true
  },
  {
    id: "isme-neu",
    name: "Viện Đào tạo Quốc tế (ISME / IBD@NEU)",
    shortName: "Viện ĐTQT ISME",
    url: "https://isme.neu.edu.vn",
    category: "thongtin",
    categoryLabel: "Thông tin & Phát triển",
    description: "Chương trình Cử nhân Quốc tế IBD liên kết các đại học hàng đầu Anh Quốc và chuyển tiếp du học.",
    features: ["Cử nhân quốc tế", "Chuyển tiếp du học", "Chương trình liên kết"],
    needs: ["xem_chuong_trinh_dao_tao"],
    isVerified: true
  },

  // Nhóm 5: Đời sống sinh viên
  {
    id: "hoisinhvien-neu",
    name: "Hội Sinh viên Trường ĐH Kinh tế Quốc dân",
    shortName: "Hội Sinh viên",
    url: "https://hoisinhvien.neu.edu.vn",
    category: "doisong",
    categoryLabel: "Đời sống sinh viên",
    description: "Cơ quan đại diện cho tiếng nói sinh viên, phong trào 'Sinh viên 5 tốt', giải bóng đá sinh viên và câu lạc bộ.",
    features: ["Danh mục các CLB", "Phong trào Sinh viên 5 tốt", "Hoạt động văn thể mỹ"],
    needs: ["tim_kiem_thong_bao"],
    isVerified: true
  }
];

export const STUDENT_NEEDS: StudentNeed[] = [
  {
    id: "xem_lich_hoc",
    title: "Xem lịch học & thời khóa biểu",
    iconName: "CalendarDays",
    description: "Tra cứu thời khóa biểu theo tuần, phòng học tại Tòa nhà A1 hoặc giảng đường B, C, D.",
    recommendedWebsiteId: "nguoihoc-neu",
    usageGuide: "Đăng nhập Cổng thông tin người học -> Chọn mục 'Tra cứu' -> 'Thời khóa biểu theo tuần' để xem chi tiết phòng học và ca học."
  },
  {
    id: "xem_lich_thi",
    title: "Xem lịch thi học kỳ",
    iconName: "FileCheck",
    description: "Tra cứu ngày thi, ca thi, số báo danh và phòng thi kết thúc học phần.",
    recommendedWebsiteId: "nguoihoc-neu",
    usageGuide: "Trước kỳ thi 2-3 tuần, vào Cổng người học -> Mục 'Lịch thi cá nhân'. Kiểm tra đúng số phòng thi và chuẩn bị thẻ sinh viên."
  },
  {
    id: "tra_cuu_diem",
    title: "Tra cứu điểm thi & CPA",
    iconName: "GraduationCap",
    description: "Xem điểm quá trình, điểm thi kết thúc học phần và điểm trung bình tích lũy CPA.",
    recommendedWebsiteId: "nguoihoc-neu",
    usageGuide: "Vào Cổng người học -> Chọn 'Kết quả học tập'. Điểm số hiển thị theo thang điểm 10 và thang điểm 4."
  },
  {
    id: "dang_ky_tin_chi",
    title: "Đăng ký tín chỉ / môn học",
    iconName: "BookOpenCheck",
    description: "Chọn lớp học phần, đăng ký lịch học các môn lý thuyết và thảo luận.",
    recommendedWebsiteId: "tinchi-neu",
    usageGuide: "Truy cập tinchi.neu.edu.vn đúng theo khung giờ mở cổng của khóa mình. Xem trước mã lớp học phần để đăng ký nhanh."
  },
  {
    id: "tim_tai_lieu_hoc_tap",
    title: "Tìm tài liệu học tập & Slide",
    iconName: "BookMarked",
    description: "Tải giáo trình môn học, bài tập về nhà và tài liệu số từ thư viện.",
    recommendedWebsiteId: "lms-neu",
    usageGuide: "Đăng nhập lms.neu.edu.vn với email trường để tải slide bài giảng; hoặc tra cứu sách mượn về tại neulib.neu.edu.vn."
  },
  {
    id: "xem_chuong_trinh_dao_tao",
    title: "Xem chương trình đào tạo",
    iconName: "Layers",
    description: "Xem danh mục các học phần bắt buộc, tự chọn và lộ trình tốt nghiệp ngành.",
    recommendedWebsiteId: "daotao-neu",
    usageGuide: "Truy cập daotao.neu.edu.vn -> Mục 'Chương trình đào tạo' -> Chọn khóa tuyển sinh và khoa quản lý để tải file khung chuẩn."
  },
  {
    id: "xin_giay_xac_nhan_sv",
    title: "Xin giấy xác nhận sinh viên",
    iconName: "FileText",
    description: "Đăng ký xin cấp giấy hoãn nghĩa vụ quân sự, vay vốn NHCSXH, làm vé xe buýt.",
    recommendedWebsiteId: "onegate-neu",
    usageGuide: "Vào Hệ thống Một cửa (onegate.neu.edu.vn) -> Chọn loại giấy tờ cần cấp -> Chọn hình thức nhận tại Phòng 105 Nhà A1."
  },
  {
    id: "kiem_tra_hoc_phi",
    title: "Kiểm tra học phí & công nợ",
    iconName: "CreditCard",
    description: "Tra cứu số tiền học phí cần nộp theo số tín chỉ đã đăng ký và hóa đơn điện tử.",
    recommendedWebsiteId: "nguoihoc-neu",
    usageGuide: "Vào Cổng người học -> Chọn mục 'Tài chính / Học phí' để xem số dư, số tiền đã gạch nợ và tải biên lai thu tiền."
  },
  {
    id: "tim_kiem_thong_bao",
    title: "Tìm kiếm thông báo của trường",
    iconName: "Bell",
    description: "Cập nhật các quyết định học bổng, lịch nghỉ lễ, thông báo học vụ khẩn cấp.",
    recommendedWebsiteId: "neu-edu-vn",
    usageGuide: "Theo dõi mục 'Thông báo' trên trang chủ neu.edu.vn hoặc fanpage chính thức 'Đại học Kinh tế Quốc dân'."
  },
  {
    id: "tim_kiem_viec_lam",
    title: "Cơ hội thực tập & việc làm",
    iconName: "Briefcase",
    description: "Tìm kiếm cơ hội thực tập tại các tập đoàn lớn, ngân hàng và doanh nghiệp đối tác.",
    recommendedWebsiteId: "jobs-neu",
    usageGuide: "Truy cập jobs.neu.edu.vn để tạo hồ sơ ứng viên và nộp đơn trực tiếp vào các vị trí thực tập sinh tuyển dụng."
  }
];
