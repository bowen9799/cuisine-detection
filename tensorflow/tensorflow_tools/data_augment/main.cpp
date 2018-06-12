#include <opencv2/opencv.hpp>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <stdlib.h>  
#include <string.h>
#include <dirent.h>
#include <unistd.h>
#include <sstream>
#include <cassert>
#include <time.h>
#include <cstddef>
#include <sys/stat.h>
#include <sys/types.h>

using namespace std;
using namespace cv;

#define TWO_PI 6.2831853071795864769252866  
int countFileNumber(const string &src){
	DIR *dir;
	struct dirent *ptr;
	int cnt = 0;
    if ((dir=opendir(src.c_str())) == NULL)
	{
		perror("Open dir error...");
		exit(1);
	} 

	while ((ptr=readdir(dir)) != NULL)
		 if(ptr->d_type == 8 || ptr->d_type == 10)    //file
			cnt++;
	return cnt;
}

double generateGaussianNoise()
{
	static bool hasSpare = false;
	static double rand1, rand2;

	if (hasSpare)
	{
		hasSpare = false;
		return sqrt(rand1) * sin(rand2);
	}

	hasSpare = true;
	rand1 = rand() / ((double)RAND_MAX);
	if (rand1 < 1e-100) rand1 = 1e-100;
	rand1 = -2 * log(rand1);
	rand2 = (rand() / ((double)RAND_MAX)) * TWO_PI;
	return sqrt(rand1) * cos(rand2);
}


void AddGaussianNoise(Mat& I)
{
	srand((int)time(0));
	// accept only char type matrices  
	CV_Assert(I.depth() != sizeof(uchar));

	int channels = I.channels();

	int nRows = I.rows;
	int nCols = I.cols * channels;

	if (I.isContinuous()) {
		nCols *= nRows;
		nRows = 1;
	}

	int i, j;
	uchar* p;
	for (i = 0; i < nRows; ++i) {
		p = I.ptr<uchar>(i);
		for (j = 0; j < nCols; ++j) {
			double val = p[j] + generateGaussianNoise() * (rand() % 40);
			if (val < 0)
				val = 0;
			if (val > 255)
				val = 255;

			p[j] = (uchar)val;

		}
	}
}

void rotImg(Mat &src, Mat &dst) {
	srand(time(0));
	double angle = rand() % 20;

	cv::Size src_sz = src.size();
	cv::Size dst_sz(src_sz.width, src_sz.height);
	int len = max(src.cols, src.rows);
	cv::Point2f center(len / 2., len / 2.);
	cv::Mat rot_mat = cv::getRotationMatrix2D(center, angle, 1.0);

	Mat dsttmp;
	cv::warpAffine(src, dsttmp, rot_mat, dst_sz);
	dst = dsttmp(Rect(0.07 * dsttmp.cols, 0.07 * dsttmp.rows, 0.83 * dsttmp.cols, 0.83 * dsttmp.rows));
}

void flipImg(Mat &src, vector<Mat> &dst) {
	assert(dst.size() == 3);
	flip(src, dst[0], -1);
	flip(src, dst[1], 1);
	flip(src, dst[2], 0);
}

void cutImg(Mat &src, Mat &dst){  
	vector<Mat> tmp(8);
	int ncols = src.cols;
	int nrows = src.rows;
	int offset[] = {ncols * 0.125, ncols * 0.11, ncols * 0.25, ncols * 0.4, nrows * 0.125,
		nrows * 0.0875, nrows * 0.11, nrows * 0.10};
	tmp[0] = src(Rect(offset[0], offset[5], ncols - offset[0] - 1, nrows - offset[5] - 1));
	tmp[1] = src(Rect(offset[1], 0, ncols - offset[1] - 1, nrows));
	tmp[2] = src(Rect(offset[3], offset[4], ncols - offset[3] - 1, nrows - offset[4] - 1));
	tmp[3] = src(Rect(0, 0, ncols - offset[3] - 1, nrows - offset[4] - 1));
	tmp[4] = src(Rect(offset[2], offset[7], ncols - offset[2]-1, nrows - offset[7]-1));
	tmp[5] = src(Rect(0, offset[7], ncols, nrows - offset[7] - 1));
	srand((int)time(0));
	tmp[rand() % 6].copyTo(dst);
}

void gaussianBlur(Mat &src, Mat &dst) {
	srand((int)time(0));
	int wsize = (1 + rand() % 4 ) * 2 + 1;
	double sigma1 = (rand() % 10) / 2.0;
	double sigma2 = (rand() % 10) / 2.0;
	GaussianBlur(src, dst, Size(wsize, wsize), sigma1, sigma2);
}

void contrastTransform(Mat &src, Mat &dst) {
	srand((int)time(0));
	double a = 0.5 + (rand() % 10) / 12.0;
	double b = (rand() % 40) - 20;
	src.convertTo(dst, -1, a, b);
}

void colorTransform(Mat &src, Mat &dst) {
	vector<Mat> vechsv;
	split(src, vechsv);
	double a = 0.8 + (rand() % 10) / 25.0;
	vechsv[1].convertTo(vechsv[1], -1, a, 0);
	merge(vechsv, dst);
}

void addGaussianNoise(Mat &img, const int& mu, const int &sigma)
{
	auto cols = img.cols*img.channels();
	auto rows = img.rows;
	random_device rd;
	mt19937 gen(rd());

	normal_distribution<> gaussR(mu, sigma);
	for (int i = 0; i < rows; i++)
	{
		auto p = img.ptr<uchar>(i);
		for (int j = 0; j < cols; j++)
		{
			auto tmp = p[j] + gaussR(gen);
			tmp = tmp > 255 ? 255 : tmp;
			tmp = tmp < 0 ? 0 : tmp;
			p[j] = tmp;
		}
	}
}

void imageGenerate(Mat &src, Mat &dst){
	srand((int)time(0));
	
	if (rand() % 2 == 1){
		vector<Mat> fimg(3);
		flipImg(src, fimg);
		int r = rand() % 3;
		cutImg(fimg[r], dst);
	}	
	else
		rotImg(src, dst);
			
	if (rand() % 2 == 1)
		contrastTransform(dst, dst);
	else if (rand() % 3 == 1)
		colorTransform(dst, dst);
	else if (rand() % 2 == 1)
		gaussianBlur(dst, dst);
	else if (rand() % 2 == 1)
		AddGaussianNoise(dst);
	//imshow("ss", dst);
	//waitKey(0);
}

void FindFiles(const string &src){
	const int maxfilenumpercls = 600;
	string dstpath = "/home/zyl/project/data_augument/result"; //save path
	DIR *dir;
	struct dirent *ptr;
    if ((dir=opendir(src.c_str())) == NULL)
	{
		perror("Open dir error...");
		exit(1);
	} 

	while ((ptr=readdir(dir)) != NULL)
	{
		static string dstsubfoldername;
		static int curnum = 0;
		if(strcmp(ptr->d_name,".")==0 || strcmp(ptr->d_name,"..")==0)    ///current dir OR parrent dir
		        continue;
		
		if(ptr->d_type == 4) {     //folder
			cout << ptr->d_name << endl;
			dstsubfoldername = dstpath + "/" + ptr->d_name;
			if (NULL == opendir(dstsubfoldername.c_str())) 
				mkdir(dstsubfoldername.c_str(), 0775);
			curnum = countFileNumber(src + "/" + ptr->d_name);
			FindFiles(src + "/" + ptr->d_name);
		}
		else if(ptr->d_type == 8 || ptr->d_type == 10)    //file
		{	
			string filename = src + "/" + ptr->d_name;
			int pos = filename.rfind('.');
			string ext = filename.substr(pos + 1, pos + 4);
			//if (ext != "jpg") continue;
			Mat imgColorSrc	= imread( filename, 1 );
			if(NULL==imgColorSrc.data || curnum >= maxfilenumpercls) continue;
			curnum++;
			Mat dst;
			imageGenerate(imgColorSrc, dst);
			stringstream ss;
			ss << curnum;
			imwrite(dstsubfoldername + "/z" + ss.str() + ".jpg", dst);
		}
	}
	closedir(dir);
}

int main(int argc, char *argv[])
{
	string imagepath = "/home/zyl/project/data_augument/image";
	FindFiles(imagepath);
}
