/**
 * Bug 反馈提交页面
 */
import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Upload,
  message,
  Space,
  Typography,
  Image,
} from 'antd';
import {
  BugOutlined,
  UploadOutlined,
  SendOutlined,
} from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { createFeedback, uploadImage } from '@/api/feedback';
import { useNavigate } from 'react-router-dom';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

const FeedbackSubmit: React.FC = () => {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploadedUrls, setUploadedUrls] = useState<string[]>([]);

  const handleUpload: UploadProps['customRequest'] = async (options) => {
    const { file, onSuccess, onError } = options;
    try {
      const response = await uploadImage(file as File);
      if (response.code === 0) {
        setUploadedUrls((prev) => [...prev, response.data.url]);
        onSuccess?.(response.data);
        message.success('图片上传成功');
      } else {
        onError?.(new Error(response.message));
        message.error(response.message || '上传失败');
      }
    } catch (error) {
      onError?.(error as Error);
      message.error('上传失败');
    }
  };

  const beforeUpload = (file: File) => {
    const isImage = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type);
    if (!isImage) {
      message.error('只能上传 JPG、PNG、GIF、WebP 格式的图片！');
      return false;
    }
    const isLt5M = file.size / 1024 / 1024 < 5;
    if (!isLt5M) {
      message.error('图片大小不能超过 5MB！');
      return false;
    }
    return true;
  };

  const handleRemove = (file: UploadFile) => {
    const index = fileList.indexOf(file);
    if (index > -1) {
      const newUrls = [...uploadedUrls];
      newUrls.splice(index, 1);
      setUploadedUrls(newUrls);
    }
  };

  const handleSubmit = async (values: any) => {
    setLoading(true);
    try {
      const response = await createFeedback({
        title: values.title,
        description: values.description,
        images: uploadedUrls.length > 0 ? uploadedUrls : undefined,
      });

      if (response.code === 0) {
        message.success('反馈提交成功，感谢您的反馈！');
        form.resetFields();
        setFileList([]);
        setUploadedUrls([]);
        // 可选：跳转到反馈列表
        // navigate('/feedback/list');
      } else {
        message.error(response.message || '提交失败');
      }
    } catch (error) {
      message.error('提交失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: 800, margin: '0 auto' }}>
      <Title level={2}>
        <BugOutlined /> Bug 反馈
      </Title>
      <Paragraph type="secondary">
        发现问题？请告诉我们！我们会尽快处理您的反馈。
      </Paragraph>

      <Card>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            label="问题标题"
            name="title"
            rules={[
              { required: true, message: '请输入问题标题' },
              { max: 200, message: '标题不能超过200个字符' },
            ]}
          >
            <Input placeholder="简要描述您遇到的问题" />
          </Form.Item>

          <Form.Item
            label="问题描述"
            name="description"
            rules={[
              { required: true, message: '请输入问题描述' },
              { min: 10, message: '描述至少需要10个字符' },
            ]}
          >
            <TextArea
              rows={6}
              placeholder="请详细描述问题，包括：&#10;1. 您在做什么操作时遇到的问题&#10;2. 预期的结果是什么&#10;3. 实际发生了什么&#10;4. 如何重现这个问题"
            />
          </Form.Item>

          <Form.Item
            label="截图（可选）"
            extra="支持 JPG、PNG、GIF、WebP 格式，单张图片不超过 5MB，最多上传 5 张"
          >
            <Upload
              listType="picture-card"
              fileList={fileList}
              customRequest={handleUpload}
              beforeUpload={beforeUpload}
              onChange={({ fileList }) => setFileList(fileList)}
              onRemove={handleRemove}
              maxCount={5}
              accept="image/jpeg,image/png,image/gif,image/webp"
            >
              {fileList.length < 5 && (
                <div>
                  <UploadOutlined />
                  <div style={{ marginTop: 8 }}>上传图片</div>
                </div>
              )}
            </Upload>
          </Form.Item>

          {uploadedUrls.length > 0 && (
            <Form.Item label="已上传的图片">
              <Image.PreviewGroup>
                <Space>
                  {uploadedUrls.map((url, index) => (
                    <Image
                      key={index}
                      width={100}
                      src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${url}`}
                    />
                  ))}
                </Space>
              </Image.PreviewGroup>
            </Form.Item>
          )}

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<SendOutlined />}
                loading={loading}
              >
                提交反馈
              </Button>
              <Button onClick={() => {
                form.resetFields();
                setFileList([]);
                setUploadedUrls([]);
              }}>
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default FeedbackSubmit;
