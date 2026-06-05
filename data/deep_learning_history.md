# Lịch sử Deep Learning

### Giai đoạn khởi nguồn 1763-1940)

Deep Learning có nguồn gốc từ những nền tảng toán học cổ điển. Năm 1763, bài luận về xác suất của Thomas Bayes được xuất bản và sau đó được Laplace hợp thức hóa vào năm 1812 thành Định lý Bayes - cốt lõi của mạng Bayes hay Belief Network . Năm 1805, lý thuyết về Least Squares ra đời, sau này trở thành hàm loss cơ bản nhất của Artificial Neural Network . [1](#page-5-0) [1](#page-5-0)

# Ý tưởng về máy "giống người" 1943-1967)

Năm 1943, nhà thần kinh học Warren McCulloch và nhà toán học Walter Pitts công bố nghiên cứu về cách não bộ con người tạo ra các mẫu phức tạp thông qua các tế bào não kết nối . Họ xây dựng một mạng neural đơn giản bằng các mạch điện, đánh dấu sự ra đời của ý tưởng về mạng nơ-ron nhân tạo . [1](#page-5-0) [1](#page-5-0)

Năm 1950, Alan Turing định hình ý niệm về Universal Machine và công bố "Computing Machinery and Intelligence" cùng với ý tưởng về Turing Test . [1](#page-5-0)

### Các mốc quan trọng:

- 1956: Cụm từ "Artificial Intelligence" lần đầu được đề cập tại hội nghị Dartmouth [1](#page-5-0)
- 1957: Frank Rosenblatt giới thiệu Perceptron một trong những nền móng đầu tiên của neural network [1](#page-5-0)
- 1958: Perceptron được phát minh phiên bản đơn giản của deep learning [2](#page-5-1)
- 1959: Arthur Samuel đưa ra khái niệm "Machine Learning" [1](#page-5-0)

# Sự phát triển của các kiến trúc 1979-1990s)

- 1979: Convolutional Neural Network được phát minh [2](#page-5-1)
- 1982: Recurrent Neural Network được phát minh để xử lý chuỗi dữ liệu cho NLP [2](#page-5-1)
- 1982-1988: Thuật toán Backpropagation ra đời do Geoffrey Hinton phát triển [1](#page-5-0)
- 1989: Reinforcement Learning được phát minh [1](#page-5-0)

Yann LeCun tạo ra LeNet5 - CNN đầu tiên được hiện thực hóa tại AT&T Bell Labs . [1](#page-5-0)

# Thời kỳ Deep Learning hiện đại 2006-nay)

Năm 2006, Geoffrey Hinton giới thiệu ý tưởng về tiền huấn luyện không giám sát thông qua deep belief nets (DBN) . Từ đây, neural networks với nhiều hidden layer được đổi tên thành "deep learning" . [1](#page-5-0) [1](#page-5-0)

#### Timeline quan trọng:

- 2009: ImageNet được giới thiệu [2](#page-5-1)
- 2010: Kaggle được ra mắt [2](#page-5-1)
- 2015: TensorFlow được Google phát hành dưới dạng open-source [1](#page-5-0)
- 2017: Kiến trúc Transformer được phát minh [2](#page-5-1)
- 2022: ChatGPT ra mắt [2](#page-5-1)

# Các Model Deep Learning Chi Tiết

# 1. Mạng Nơ-ron Cổ điển Classical Neural Networks)

Được thiết kế bởi Frank Rosenblatt năm 1958, sử dụng kiến trúc mạng kết nối đầy đủ từ các perceptron đa tầng . Sử dụng các hàm kích hoạt như: [3](#page-5-2)

- Hàm tuyến tính
- Hàm phi tuyến: sigmoid, tanh và ReLU [3](#page-5-2)

Phù hợp với dữ liệu có cấu trúc bảng và các bài toán phân loại, hồi quy với đầu vào là giá trị số thực . [3](#page-5-2)

### 2. Convolutional Neural Networks CNN)

CNN sử dụng phép toán tích chập để tạo liên kết giữa các layers . Mỗi neuron chỉ kết nối đến một vài neurons đại diện thay vì tất cả, giúp học được các mối liên hệ không gian của dữ liệu tốt hơn . [4](#page-5-3) [4](#page-5-3)

Ứng dụng chính: Computer Vision như phân loại hình ảnh, phát hiện đối tượng [4](#page-5-3)

Kiến trúc CNN kinh điển: VGG, ResNet, MobileNet, InceptionNet, YOLO, SSD [4](#page-5-3)

# 3. Recurrent Neural Networks RNN)

RNN phù hợp với dữ liệu có mối liên hệ về thời gian như time series forecasting và NLP . Một phần output ở thời điểm hiện tại được đưa trở lại thành input ở thời điểm tiếp theo, giúp ghi nhớ thông tin trong quá khứ . [4](#page-5-3) [4](#page-5-3)

#### Các kiến trúc RNN kinh điển:

- LSTM Long Short-Term Memory): Có khả năng học tập và lưu trữ thông tin lâu dài [5](#page-5-4)
- GRU Gated Recurrent Unit) [4](#page-5-3)

# 4. Generative Adversarial Networks GAN)

GAN gồm hai mạng cạnh tranh nhau : [6](#page-5-5)

- Generator: Tạo ra dữ liệu giả
- Discriminator: Phát hiện dữ liệu giả và dữ liệu thật

### Ứng dụng phổ biến:

- Tạo khuôn mặt người
- Thay đổi độ tuổi khuôn mặt
- Sinh ảnh vật thể
- Tạo nhân vật hoạt hình
- Deepfake và DALL-E [3](#page-5-2) [6](#page-5-5)

#### 5. Autoencoders

Gồm hai thành phần chính : [4](#page-5-3)

Encoder: Mã hóa input thành vector trong không gian ít chiều hơn

Decoder: Giải mã để xây dựng lại dữ liệu ban đầu

Ứng dụng: Giảm chiều dữ liệu, nén dữ liệu, phân tích dữ liệu [4](#page-5-3) [5](#page-5-4)

### 6. Transformer Networks

Transformer là thuật toán đột phá giúp xử lý dữ liệu tuần tự hiệu quả hơn RNN và LSTM nhờ cơ chế Attention . [6](#page-5-5)

#### Cấu trúc chính:

Cơ chế tự chú ý (Self-Attention): Tập trung vào các phần quan trọng của dữ liệu [6](#page-5-5)

Ứng dụng: ChatGPT, Google Translate, phân tích dữ liệu lớn, tổng hợp văn bản [6](#page-5-5)

### 7. Deep Reinforcement Learning

Mô phỏng quá trình học tập của con người, trong đó các tác tử (agent) tương tác với môi trường để thay đổi trạng thái và đạt mục tiêu . [7](#page-5-6)

Ứng dụng: Game cờ vua, poker, xe tự lái, robot [7](#page-5-6)

Biến thể quan trọng: Deep Q-Networks (DQN) được sử dụng trong tối ưu hóa chiến lược trò chơi điện tử [5](#page-5-4)

### 8. Các Model Khác

- Boltzmann Machine: Mạng không có hướng xác định, các node liên kết thành hình tròn, dùng để tạo tham số cho mô hình [7](#page-5-6)
- Deep Belief Networks DBN): Có khả năng học tập và trích xuất đặc trưng từ dữ liệu [5](#page-5-4)
- Capsule Networks: Phân tích dữ liệu theo mối quan hệ giữa các đặc trưng [5](#page-5-4)

# Nhân tố thành công của Deep Learning

Sự bùng nổ của deep learning trong 5-6 năm gần đây do : [8](#page-5-7)

- Sự ra đời của các bộ dữ liệu lớn được gán nhãn
- Khả năng tính toán song song tốc độ cao của GPU

- Sự ra đời của ReLU và các hàm kích hoạt hạn chế vanishing gradient
- Cải tiến kiến trúc: GoogLeNet, VGG, ResNet và kỹ thuật transfer learning
- Các kỹ thuật regularization mới: dropout, batch normalization, data augmentation

# Các Papers Nổi Tiếng và Quan Trọng Trong Lịch Sử Deep Learning

### Giai đoạn Khởi nguồn 1950-1970s)

#### "Computing Machinery and Intelligence" 1950)

- Tác giả: Alan Turing
- Đóng góp: Giới thiệu Turing Test tiêu chuẩn đánh giá trí tuệ nhân tạo của máy [9](#page-5-8)

#### "Perceptrons" 1958)

- Tác giả: Frank Rosenblatt
- Đóng góp: Giới thiệu khái niệm perceptron mô hình toán học đơn giản của mạng nơ-ron [9](#page-5-8)

#### "The Logic Theorist" 1956)

- Tác giả: Allen Newell, J. C. Shaw, và Herbert Simon
- Đóng góp: Mô tả chương trình có thể chứng minh định lý toán học bằng kỹ thuật AI [9](#page-5-8)

# Thời kỳ Phát triển Nền tảng 1980s-1990s)

#### "Learning Internal Representations by Error Propagation" 1987)

Đóng góp: Phát triển thuật toán backpropagation cho Deep Neural Networks [10](#page-5-9)

### "Backpropagation Applied to Handwritten Zip Code Recognition" 1989)

Đóng góp: Ứng dụng đầu tiên của CNN trong nhận dạng chữ viết tay [10](#page-5-9)

### "Continually Running Fully Recurrent Neural Networks" 1989)

Đóng góp: Nền tảng cho Recurrent Neural Networks [10](#page-5-9)

### "A Simple Weight Decay Can Improve Generalization" 1991)

Đóng góp: Kỹ thuật regularization để cải thiện khả năng tổng quát hóa [10](#page-5-9)

### "Long-Short Term Memory" 1997)

Đóng góp: Giới thiệu LSTM để giải quyết vấn đề vanishing gradient trong RNN [10](#page-5-9)

### "Gradient-Based Learning Applied to Document Recognition" 1998)

Tác giả: Yann LeCun et al.

Đóng góp: Giới thiệu LeNet-5 - CNN bảy tầng đầu tiên, cách mạng hóa nhận dạng ký tự và hình ảnh [11](#page-5-10) [10](#page-5-9)

### Thời kỳ Renaissance Deep Learning 2000s-2012)

#### "Deep Sparse Rectified Neural Networks" 2011)

Đóng góp: Giới thiệu hàm kích hoạt ReLU, giải quyết vấn đề vanishing gradient [10](#page-5-9)

### "ImageNet Classification with Deep Convolutional Networks" 2012)

- Tác giả: Alex Krizhevsky, Ilya Sutskever, và Geoffrey Hinton
- Đóng góp: AlexNet CNN đầu tiên thắng ImageNet với top-5 error 15.4% (so với 26.2% của phương pháp truyền thống)
- Tầm quan trọng: Được cite 6,184 lần, đánh dấu bước ngoặt của Deep Learning [12](#page-5-11)

# Thời kỳ Bùng nổ 2013-2017)

#### "Word Representations in Vector Space" 2013)

Đóng góp: Giới thiệu Word2Vec, cách mạng hóa xử lý ngôn ngữ tự nhiên [10](#page-5-9)

#### "Auto-Encoding Variational Bayes" 2013)

Đóng góp: Phát triển Variational Autoencoders (VAE) [10](#page-5-9)

#### "Generative Adversarial Networks" 2014)

- Tác giả: Ian Goodfellow et al.
- Đóng góp: Giới thiệu GAN cách mạng trong sinh dữ liệu [10](#page-5-9)

### "Sequence to Sequence Learning" 2014)

Đóng góp: Phát triển kiến trúc Seq2Seq cho machine translation [10](#page-5-9)

### "Neural Machine Translation with Alignment" 2014)

Đóng góp: Giới thiệu cơ chế Attention đầu tiên [10](#page-5-9)

# "Adam: A Method for Stochastic Optimization" 2014)

Đóng góp: Thuật toán tối ưu Adam, trở thành chuẩn trong training neural networks [10](#page-5-9)

# "Preventing Neural Networks from Overfitting" 2014)

Đóng góp: Kỹ thuật Dropout để giảm overfitting [10](#page-5-9)

# Thời kỳ Transformer và AI hiện đại 2017-nay)

#### "Attention Is All You Need" 2017)

- Tác giả: Ashish Vaswani et al.
- Đóng góp: Giới thiệu kiến trúc Transformer, loại bỏ hoàn toàn RNN và CNN

Tầm quan trọng: Nền tảng cho tất cả các LLM hiện đại như ChatGPT và Claude, cách mạng hóa NLP với khả năng xử lý song song và học long-range dependencies hiệu quả hơn [13](#page-5-12)

# Các Papers về Kiến trúc CNN Tiên phong

#### VGG Networks, ResNet, và các kiến trúc CNN khác

Đóng góp: Phát triển các kiến trúc CNN sâu hơn và hiệu quả hơn sau thành công của AlexNet [12](#page-5-11)

#### Contributions của Geoffrey Hinton

Geoffrey Hinton có nhiều đóng góp quan trọng được ghi nhận trong các papers:

- Backpropagation: Phát triển thuật toán huấn luyện neural networks
- Restricted Boltzmann Machines: Nền tảng cho deep learning
- Deep Learning architectures: Kiến trúc mạng sâu
- Capsule Networks: Khắc phục hạn chế của CNN [14](#page-5-13)

Các papers này đã định hình lịch sử và phát triển của Deep Learning, từ những ý tưởng cơ bản về AI cho đến các breakthrough hiện đại tạo nền tảng cho ChatGPT và các hệ thống AI tiên tiến ngày nay . [15](#page-5-14)

- <span id="page-5-2"></span><span id="page-5-1"></span><span id="page-5-0"></span>1. <https://cntt.ntt.edu.vn/hoat-dong/sinh-vien/lich-su-deep-learning-dl/>
- <span id="page-5-3"></span>2. <https://getthematic.com/insights/what-is-deep-learning/>
- <span id="page-5-4"></span>3. <https://www.bkns.vn/ki-thuat-deep-learning.html>
- <span id="page-5-5"></span>4. [https://tiensu.github.io/blog/19\\_deep\\_learning\\_algorithms\\_summary/](https://tiensu.github.io/blog/19_deep_learning_algorithms_summary/)
- <span id="page-5-6"></span>. <https://g-customer360.com/thuat-toan-deep-learning-khong-the-bo-qua/>
- <span id="page-5-7"></span>6. <https://tokyotechlab.com/vi/blogs/what-is-deep-learning>
- <span id="page-5-8"></span>. <https://vietnix.vn/deep-learning-la-gi/>
- 8. <https://machinelearningcoban.com/2018/06/22/deeplearning/>
- <span id="page-5-9"></span>9. [https://www.reddit.com/r/MachineLearning/comments/zetvmd/d\\_if\\_you\\_had\\_to\\_pick\\_1020\\_significant\\_p](https://www.reddit.com/r/MachineLearning/comments/zetvmd/d_if_you_had_to_pick_1020_significant_papers_that/) [apers\\_that/](https://www.reddit.com/r/MachineLearning/comments/zetvmd/d_if_you_had_to_pick_1020_significant_papers_that/)
- <span id="page-5-10"></span>10. <https://saurabhalone.com/blog/dl-papers/deep>
- <span id="page-5-11"></span>11. [https://quantumzeitgeist.com/yann-lecun-the-french-ai-pioneer-behind-the-convolutional-neural-netw](https://quantumzeitgeist.com/yann-lecun-the-french-ai-pioneer-behind-the-convolutional-neural-network/) [ork/](https://quantumzeitgeist.com/yann-lecun-the-french-ai-pioneer-behind-the-convolutional-neural-network/)
- <span id="page-5-13"></span><span id="page-5-12"></span>12. <https://adeshpande3.github.io/The-9-Deep-Learning-Papers-You-Need-To-Know-About.html>
- <span id="page-5-14"></span>13. <https://briancartergroup.com/the-groundbreaking-transformer-paper-attention-is-all-you-need/>
- 14. [https://papers.ssrn.com/sol3/papers.cfm?abstract\\_id=4980068](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4980068)
- 1. education.academic\_assistance