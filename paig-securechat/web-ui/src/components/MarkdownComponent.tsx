import ContentCopyOutlinedIcon from '@mui/icons-material/ContentCopyOutlined';
import DoneOutlinedIcon from '@mui/icons-material/DoneOutlined';
import { Typography, styled } from '@mui/material';
import Box from '@mui/material/Box/Box';
import React, { FC, memo, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import { Button } from '@mui/material';
import rehypeMathjax from 'rehype-mathjax';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';

interface Props {
  language: string;
  value: string;
}

const formatString = (str: string) => str.replace(/\n\n/g, '\n');

const CodeBlock: FC<Props> = memo(({ language, value }) => {
  const [isCopied, setIsCopied] = useState<Boolean>(false);

  const copyToClipboard = () => {
    if (!navigator.clipboard || !navigator.clipboard.writeText) {
      return;
    }

    navigator.clipboard.writeText(value).then(() => {
      setIsCopied(true);

      setTimeout(() => {
        setIsCopied(false);
      }, 2000);
    });
  };
  return (
    <Box sx={{ fontFamily: 'sans-serif', fontSize: '16px' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', py: 1.5, px: 4 }}>
        <Typography sx={{ fontSize: 'xs', textTransform: 'lowercase', color: 'white' }}>{language}</Typography>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Button
            sx={{ display: 'flex', gap: 1.5, alignItems: 'center', borderRadius: 'rounded', bg: 'none', p: 1, fontSize: 'xs', color: 'white' }}
            onClick={copyToClipboard}
          >
            {isCopied ? <DoneOutlinedIcon /> : <ContentCopyOutlinedIcon />}
          </Button>
        </Box>
      </Box>

      <SyntaxHighlighter language={language} style={oneDark} customStyle={{ margin: 0 }}>
        {value}
      </SyntaxHighlighter>
    </Box>
  );
});
const StyledMarkdown = styled(ReactMarkdown)`
  & p {
    padding-top: 8px;
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 0;
  }

  * {
    word-wrap: break-word;
  }
`;

const MarkdownComponent = ({ content }: { content: string }) => {
  return (
    <Box>
      <StyledMarkdown
        components={{
          code({ node, inline, className, children, ...props }) {
            if (children.length) {
              if (children[0] == '▍') {
                return <span className='animate-pulse cursor-default mt-1'>▍</span>;
              }

              children[0] = (children[0] as string).replace('`▍`', '▍');
            }

            const match = /language-(\w+)/.exec(className || '');

            return !inline ? (
              <CodeBlock key={Math.random()} language={(match && match[1]) || ''} value={String(children).replace(/\n$/, '')} {...props} />
            ) : (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          table({ children }) {
            return <table className='border-collapse border border-black px-3 py-1 dark:border-white'>{children}</table>;
          },
          th({ children }) {
            return <th className='break-words border border-black bg-gray-500 px-3 py-1 text-white dark:border-white'>{children}</th>;
          },
          td({ children }) {
            return <td className='break-words border border-black px-3 py-1 dark:border-white'>{children}</td>;
          },
        }}
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeMathjax]}
      >
        {formatString(content)}
      </StyledMarkdown>
    </Box>
  );
};

export default MarkdownComponent;
