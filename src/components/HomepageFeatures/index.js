import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: '这是什么？',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        课栈是一群 ECNU 学生自发组织与构建的课程资料共享项目，为的是收集与整合学校各专业、课程的学习资料，以帮助后来的学生更好地度过学校生活。
      </>
    ),
  },
  {
    title: '怎么使用？',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        使用左上角查阅目录，寻找自己希望查询的课程以浏览。或者右上角直接搜索课程、专业名称或关键字。如果缺少想要的资料，还请等待后续更新，或者将自己的资料上传上来，敬请期待。
      </>
    ),
  },
  {
    title: '我也有资料想要贡献！',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        如果您会使用Github的话，可以在我们的仓库中新建issue与PR提交，文件可存放在个人网盘(如百度网盘)等地方。如果不便使用，还可以联系zy1834576129@outlook.com，以“课栈资料贡献：[学院][专业][课程]”的格式作为主题发送邮件，我们自己整理上传。
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
