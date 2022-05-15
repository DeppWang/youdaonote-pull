**4. 面向对象**

1. 面向对象思想

&emsp;1.1 面向过程

&emsp;1.2 面向对象

2. 类与对象及其使用

3. 成员变量和局部变量的区别

4. 对象的内存图

&emsp;4.1 对象和方法

&emsp;4.2 形式参数问题

5. 匿名对象

&emsp;5.1 概念

&emsp;5.2 匿名对象的两种使用情况

&emsp;5.3 好处

6. 封装(private)

&emsp;6.1 概述

&emsp;6.2 private关键字

7. this关键字

8. 构造方法

&emsp;8.1 构造方法作用概述

&emsp;8.2 类的成员方法

&emsp;8.3 标准类

9.类的初始化过程

10. static关键字（静态）

&emsp;10.1 概念

&emsp;10.2 static关键字特点

&emsp;10.3 static关键字注意事项

&emsp;10.6 main方法解读

&emsp;11.1 制作帮助文档

&emsp;11.2 如何使用帮助文档

&emsp;11.3 根据文档编辑一个Math.random

12 代码块

&emsp;12.1 局部代码块

&emsp;12.2 构造代码块

&emsp;12.3 静态代码块

&emsp;12.4 类执行顺序

**1. 面向对象思想**



**1.1 面向过程**

&emsp;我们来回想一下，这几天我们完成一个需求的步骤：<span style='color:#df402a'>首先是搞清楚我们要做什么，然后在分析怎么做，最后我们再代码体现。</span>也就是一步一步去实现，而具体的每一步都需要我们去实现和操作。这些步骤相互调用和协作，完成我们的需求。

&emsp;在上面的每一个具体步骤中我们都是<span style='color:#df402a'>参与者</span>，并且需要面对具体的每一个步骤和过程，这就是面向过程最直接的体现。

&emsp;那么什么是面向过程开发呢?面向过程就是分析出解决问题所需要的步骤，然后用<span style='color:#df402a'>函数</span>把这些步骤一步一步实现，使用的时候一个一个依次调用就可以了。

&emsp;面向过程的代表语言：**C语言**



**1.2 面向对象**

&emsp;当需求比较简单时，我们一步一步去操作没问题，并且效率也挺高。可随着需求的更改，功能的增多，发现需要面对每一个步骤很麻烦了，这时就开始思索，能不能把这些步骤和功能在进行封装，封装时根据不同的功能，进行不同的封装，功能类似的封装在一起。这样结构就清晰了很多。用的时候，找到对应的类就可以了。这就是面向对象的思想。接下来我们看看面向对象到底是什么?

&emsp;面向对象是**<span style='color:#df402a'>把构成问题事务分解成各个对象，建立对象的目的不是为了完成一个步骤，而是为了描叙某个事物在整个解决问题的步骤中的行为。</span>** 

&emsp;使用面向对象思想解决问题的时候，只需要以一个指挥者的身份，去调用不同的对象的行为去完成事情即可。



**概述**

&emsp;面向对象编程，即<span style='color:#FAE220'>OOP</span>，是一种编程范式

&emsp;面向对象是基于面向过程的编程思想

&emsp;面向对象是基于万物皆对象这个哲学观点的



**特点**

&emsp;是一种更符合我们思想习惯的思想

&emsp;可以将复杂的事情简单化

&emsp;将我们从执行者变成了指挥者

&emsp;&emsp;角色发生了转换



**使用规则**

&emsp;在用面向对象思想体现的时候，给出一个三句话使用规则，让我们更符合面向对象思想

&emsp;A:首先分析有那些对象（类）

&emsp;B:接着分析每个对象（类）应该有什么

&emsp;C:最后分析对象（类）与对象（类）的关系



**开发&设计&特征**

&emsp;面向对象开发

&emsp;就是不断的创建对象，使用对象，指挥对象做事情。

&emsp;面向对象设计

&emsp;其实就是在分析、管理和维护对象之间的关系。

&emsp;面向对象特征

&emsp;&emsp;封装(encapsulation)

&emsp;&emsp;继承(inheritance)

&emsp;&emsp;多态(polymorphism)







**2. 类与对象及其使用**

&emsp;类只能被public protected defult 3种修饰，不能被private修饰



**类与对象关系**

&emsp;我们学习编程语言，就是为了模拟现实世界的事物，实现信息化。比如：去超市买东西的计费系统，去银行办业务的系统。

&emsp;我们如何表示一个现实世界事物呢：

&emsp;&emsp;属性 就是该事物的描述信息

&emsp;&emsp;行为 就是该事物能够做什么

&emsp;&emsp;举例：学生事物

&emsp;我们如何使用Java语言来映射现实世界事务呢？

&emsp;我们学习的Java语言最基本单位是类，所以，我们就应该把事物用一个类来体现。



**类与对象关系**

&emsp;类

&emsp;是一组相关的属性和行为的集合，是一种抽象概念

&emsp;对象

&emsp;是该类事物的具体体现

&emsp;类和对象的关系

&emsp;&emsp;类的具体表现或者实例就是对象

&emsp;&emsp;对象的抽象或者总概括就是类。







现实世界的事物

&emsp;属性 人的身高，体重等

&emsp;行为 人可以学习，吃饭等

Java中用class描述事物也是如此

&emsp;成员变量 就是事物的属性

&emsp;成员方法 就是事物的行为

定义类其实就是定义类的成员(成员变量和成员方法)

&emsp;<span style='color:#df402a'>成员变量：和以前定义变量是一样的，只不过位置发生了改变。在类中方法外。</span>

&emsp;<span style='color:#df402a'>成员方法：和以前定义方法是一样的，只不过把static去掉，后面在详细讲解static的作用。</span>



**3. 成员变量和局部变量的区别**

在类中的位置不同

&emsp;**成员变量：** 类中方法外

&emsp;**局部变量：** 方法内或者方法声明上



在内存中的位置不同

&emsp;**成员变量** <span style='color:#df402a'>堆内存</span>

&emsp;**局部变量 **<span style='color:#df402a'>栈内存</span>



生命周期不同

&emsp;成员变量 随着对象的存在而存在，随着对象的消失而消失

&emsp;局部变量 随着方法的调用而存在，随着方法的调用完毕而消失



初始化值不同

&emsp;成员变量 有默认的初始化值

&emsp;局部变量 没有默认的初始化值，必须先定义，赋值，才能使用。



**注意**

&emsp;<span style='color:#df402a'>成员变量和局部变量可以重名，但是以局部变量优先。首先遵循的是代码的执行顺序</span>

&emsp;<span style='color:#df402a'>（局部变量在栈上！成员变量在堆上，先找栈上的。）</span>

**<span style='color:#7f0055'>public</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>class</span>** <span style='color:#393939'>Student {</span>    <span style='color:#393939'> </span><span style='color:#3f7f5f'>// 成员变量</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>int</span>**<span style='color:#393939'> </span><span style='color:#0000c0'>age</span><span style='color:#393939'>;</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>public</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>void</span>** <span style='color:#393939'>method() {</span>        <span style='color:#393939'> </span><span style='color:#3f7f5f'>// 给成员变量重新赋值</span>        <span style='color:#393939'> </span><span style='color:#0000c0'>age</span> <span style='color:#393939'>= 30;</span>        <span style='color:#393939'> </span><span style='color:#3f7f5f'>// 局部变量</span>        <span style='color:#393939'> </span>**<span style='color:#7f0055'>int</span>**<span style='color:#393939'> </span><span style='color:#6a3e3e'>age</span> <span style='color:#393939'>= 20;</span>         <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span>**<span style='color:#7f0055'>this</span>**<span style='color:#393939'>.</span><span style='color:#0000c0'>age</span><span style='color:#393939'>);</span>         <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#6a3e3e'>age</span><span style='color:#393939'>);</span>     <span style='color:#393939'>}</span> <span style='color:#393939'>}</span>



**4. 对象的内存图**



**4.1 对象和方法**



&emsp;**<span style='color:#df402a'>成员的对象的值每个都是一份，</span>**

&emsp;**<span style='color:#df402a'>但是同一类的对象，用的方法都是同一个！！</span>**

&emsp;**<span style='color:#df402a'>方法执行完，方法栈中的值都销毁了，但是方法区中的方法不销毁，因为是大家共用的。</span>**

**<span style='color:#7f0055'>public</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>class</span>** <span style='color:#393939'>PhoneDome {</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>public</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>static</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>void</span>** <span style='color:#393939'>main(String[] </span><span style='color:#6a3e3e'>args</span><span style='color:#393939'>) {</span>         <span style='color:#393939'>Phone </span><span style='color:#6a3e3e'>p</span> <span style='color:#393939'>= </span>**<span style='color:#7f0055'>new</span>** <span style='color:#393939'>Phone();</span>         <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#6a3e3e'>p</span><span style='color:#393939'>); </span><span style='color:#3f7f5f'>//地址值</span>         <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#6a3e3e'>p</span><span style='color:#393939'>.setBrand);</span><span style='color:#3f7f5f'>//地址值</span>      <span style='color:#393939'>}</span> <span style='color:#393939'>}</span>





**4.2 形式参数问题**



基本类型作为形式参数

&emsp;传递的是<span style='color:#df402a'>值</span>

引用类型作为形式参数

&emsp;传递的是<span style='color:#df402a'>堆内存的地址</span>

&emsp;如果想传递堆内存的地址，只有new的东西，在堆里面才分配空间，也就是说使用引用类型作为形式参数的话，需要传递类的对象。



**5. 匿名对象**



**5.1 概念**

&emsp;匿名对象：就是没有名字的对象。是对象的一种简化表示形式



**5.2 匿名对象的两种使用情况**

&emsp;**1. 对象调用方法仅仅一次的时候**(可以理解为专属对象)

<span style='color:#769436'>new StudentDome().method(s);</span>

&emsp;**2. 作为实际参数传递**

<span style='color:#769436'>new StudentDome().method(new Student());</span>



**5.3 好处**

&emsp;1. 书写简单

&emsp;2. 节省栈内存空间

&emsp;3 . 加快对象的销毁（使用GC回收的时候，他会判断该对象有没有引用指向他）

&emsp;&emsp;有，匿名对象调用完毕就是垃圾。可以被垃圾回收器回收。 带名字的对象被调用完以后不会被回收，还是要和对象s连着

注意事项

&emsp;(1).我们一般不会用匿名对象给属性赋值，无法获取属性值。

&emsp;(2).创建出来每一次都是一个新的对象。<span style='color:#df402a'>想调用多次的时候，不适合</span>。



**6. 封装(private)**

**6.1 概述**

&emsp;是指隐藏对象的属性和实现细节，仅对外提供公共访问方式。

**好处：**

&emsp;隐藏实现细节，提供公共的访问方式

&emsp;提高了代码的复用性

&emsp;提高安全性。



**封装原则：**

&emsp;将不需要对外提供的内容都隐藏起来。

&emsp;把属性隐藏，提供公共方法对其访问。



**6.2 private关键字**

&emsp;是一个权限修饰符。

&emsp;可以修饰成员(成员变量和成员方法)

&emsp;被private修饰的成员只在本类中才能访问。



**private最常见的应用：**

&emsp;把成员变量用private修饰

&emsp;提供对应的getXxx()/setXxx()方法

&emsp;一个标准的案例的使用



**7. this关键字**

this:代表所在类的对象引用

记住：

&emsp;方法被哪个对象调用，this就代表那个对象

什么时候使用this呢?

&emsp;局部变量隐藏成员变量

&emsp;其他用法后面和super一起讲解



**作用：**

&emsp;使用this关键字， 就可以在就局部优先的规则影响下，去访问到优先级别低的成员变量



**8. 构造方法**

**8.1 构造方法作用概述**

&emsp;给对象的数据进行初始化

**构造方法格式**

&emsp;方法名与类名相同

&emsp;没有返回值类型，连void都没有

&emsp;没有具体的返回值



**作用：**

&emsp;给成员变量初始化的。

//成员<span style='color:#769436'>方法 pub</span>l<span style='color:#769436'>ic void setName(String name){ this</span>.<span style='color:#769436'>name = name; }</span>

**构造方法注意事项**

&emsp;如果你不提供构造方法，系统会给出默认构造方法

&emsp;如果你提供了构造方法，系统将不再提供<span style='color:#df402a'>（若你这个时候没有定义一个无参的构造方法，容易出现构造方法异常）</span>

&emsp;构造方法也是可以重载的

&emsp;<span style='color:#df402a'>构造方法执行过程中可以执行类的别的方法</span>



&emsp;**<span style='color:#df402a'>如果构造方法是私有构造方法，那么只能直接调用，不能new对象方式来调用</span>**

&emsp;&emsp;可以防止该类创建对象

&emsp;&emsp;通常在工具类中使用

**<span style='color:#7f0055'>public</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>class</span>** <span style='color:#393939'>Student {</span>    <span style='color:#393939'> </span><span style='color:#3f7f5f'>// 成员变量</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>private</span>** <span style='color:#393939'>String </span><span style='color:#0000c0'>name</span><span style='color:#393939'>;</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>private</span>** <span style='color:#393939'>String </span><span style='color:#0000c0'>sex</span><span style='color:#393939'>;</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>private</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>int</span>**<span style='color:#393939'> </span><span style='color:#0000c0'>age</span><span style='color:#393939'>;</span>    <span style='color:#393939'> </span><span style='color:#3f7f5f'>// 构造方法</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>public</span>** <span style='color:#393939'>Student() {</span>         <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#2a00ff'>"无参构造"</span><span style='color:#393939'>);</span>     <span style='color:#393939'>}</span>    <span style='color:#393939'> </span><span style='color:#3f7f5f'>// 有参构造方法</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>public</span>** <span style='color:#393939'>Student(String </span><span style='color:#6a3e3e'>name</span><span style='color:#393939'>, String </span><span style='color:#6a3e3e'>sex</span><span style='color:#393939'>, </span>**<span style='color:#7f0055'>int</span>**<span style='color:#393939'> </span><span style='color:#6a3e3e'>age</span><span style='color:#393939'>) {</span>         <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#2a00ff'>"有参构造"</span><span style='color:#393939'>);</span>        <span style='color:#393939'> </span>**<span style='color:#7f0055'>this</span>**<span style='color:#393939'>.</span><span style='color:#0000c0'>name</span> <span style='color:#393939'>= </span><span style='color:#6a3e3e'>name</span><span style='color:#393939'>;</span>        <span style='color:#393939'> </span>**<span style='color:#7f0055'>this</span>**<span style='color:#393939'>.</span><span style='color:#0000c0'>sex</span> <span style='color:#393939'>= </span><span style='color:#6a3e3e'>sex</span><span style='color:#393939'>;</span>        <span style='color:#393939'> </span>**<span style='color:#7f0055'>this</span>**<span style='color:#393939'>.</span><span style='color:#0000c0'>age</span> <span style='color:#393939'>= </span><span style='color:#6a3e3e'>age</span><span style='color:#393939'>;</span>     <span style='color:#393939'>}</span> <span style='color:#393939'>}</span>



**<span style='color:#7f0055'>public</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>class</span>** <span style='color:#393939'>Student {</span>    <span style='color:#393939'> </span><span style='color:#3f7f5f'>// 私有构造方法，这样别人不能通过new对象方式调用</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>private</span>** <span style='color:#393939'>Student() {</span>         <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#2a00ff'>"私有无参构造"</span><span style='color:#393939'>);</span>     <span style='color:#393939'>}</span> <span style='color:#393939'>}</span>



**8.2 类的成员方法**

成员方法其实就是我们前面讲过的方法

方法具体划分：

&emsp;根据返回值

&emsp;&emsp;有明确返回值方法

&emsp;&emsp;返回void类型的方法

&emsp;根据形式参数

&emsp;&emsp;无参方法

&emsp;&emsp;带参方法



**8.3 标准类**

**类的组成**

&emsp;成员变量

&emsp;成员方法

&emsp;构造方法



**<span style='color:#df402a'>一个基本类的标准代码写法：</span>**

**类**

&emsp;成员变量

&emsp;构造方法

&emsp;&emsp;无参构造方法

&emsp;&emsp;带参构造方法

&emsp;成员方法

&emsp;&emsp;getXxx()

&emsp;&emsp;setXxx()

**给成员变量赋值的方式**

&emsp;无参构造方法+setXxx()

&emsp;带参构造方法



**9.类的初始化过程**



**Student s = new Student();在内存中做了哪些事情?**



**Student**

&emsp;加载Student.class文件进内存<span style='color:#e66c00'>(方法区)</span>

<span style='color:#e66c00'>new</span>

&emsp;在栈内存为s开辟空间

&emsp;在堆内存为学生对象开辟空间

stdent() 其实这个都是在jvm里面隐含的

&emsp;对学生对象的成员变量进行<span style='color:#df402a'>默认初始化（null 0）</span>

&emsp;对学生对象的成员变量进行<span style='color:#df402a'>显示初始化</span>

&emsp;通过<span style='color:#df402a'>构造方法</span>对学生对象的成员变量赋值

s = **new Student();**

&emsp;学生对象初始化完毕，把<span style='color:#df402a'>对象地址</span>赋值给s变量

**<span style='color:#7f0055'>class</span>** <span style='color:#393939'>Student{    </span>priva**<span style='color:#7f0055'>te Stri</span>**<span style='color:#393939'>ng name </span><span style='color:#0000c0'>= "社</span><span style='color:#393939'>会我王</span><span style='color:#2a00ff'>婶";    </span><span style='color:#393939'> </span>p<span style='color:#393939'>riva</span>**<span style='color:#7f0055'>te int </span>**<span style='color:#393939'>a</span>**<span style='color:#7f0055'>ge </span>**<span style='color:#393939'>=</span> <span style='color:#0000c0'>30</span><span style='color:#393939'>;     </span>p<span style='color:#393939'>ubli</span>**<span style='color:#7f0055'>c Stud</span>**<span style='color:#393939'>ent(){     </span>    <span style='color:#393939'>//这里</span><span style='color:#df402a'>其实是jvm给你隐含了几步“     </span>    <span style='color:#393939'>// 4：对象成员变量默认初始化（null</span> <span style='color:#df402a'>0）     </span>    <span style='color:#393939'>// 5：对象成员变量显式初始化     </span>    <span style='color:#393939'>// 6：对象成员变量构造方法初始化     </span>    <span style='color:#393939'>//如果构</span><span style='color:#3f7f5f'>造方法比成员变量显示初始化要早，那么此处应该输出null     </span>    <span style='color:#393939'>System.out.p</span>**<span style='color:#0000c0'>rin</span>**<span style='color:#393939'>tln(name)</span><span style='color:#0000c0'>;   </span> <span style='color:#393939'> </span>    <span style='color:#393939'>name </span><span style='color:#0000c0'>= "大</span><span style='color:#393939'>唐小姐</span><span style='color:#2a00ff'>姐";    </span><span style='color:#393939'> </span>    <span style='color:#393939'>age =</span> <span style='color:#0000c0'>31</span><span style='color:#393939'>;     </span>    <span style='color:#393939'>System.out.p</span>**<span style='color:#0000c0'>rin</span>**<span style='color:#393939'>tln(name)</span><span style='color:#0000c0'>;   </span> <span style='color:#393939'> </span>}    <span style='color:#393939'> </span>p<span style='color:#393939'>ubli</span>**<span style='color:#7f0055'>c void</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>show</span>**<span style='color:#393939'>(){     </span>    <span style='color:#393939'>System.out.p</span>**<span style='color:#0000c0'>rin</span>**<span style='color:#393939'>tln(name+</span><span style='color:#0000c0'>"--"</span><span style='color:#393939'>+</span><span style='color:#2a00ff'>age)</span><span style='color:#393939'>;</span>  <span style='color:#0000c0'> </span> <span style='color:#393939'> </span>} <span style='color:#393939'>} cl</span>a<span style='color:#393939'>s</span>s **<span style='color:#7f0055'>Clas</span>**<span style='color:#393939'>sInitDemo{     </span>p<span style='color:#393939'>ubli</span>**<span style='color:#7f0055'>c stat</span>**<span style='color:#393939'>i</span>**<span style='color:#7f0055'>c void</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>main</span>**<span style='color:#393939'>(String[] args)</span><span style='color:#6a3e3e'>{   </span> <span style='color:#393939'> </span>    <span style='color:#393939'>//创建对</span><span style='color:#3f7f5f'>象     </span>    <span style='color:#393939'>Student s = n</span><span style='color:#6a3e3e'>e</span><span style='color:#393939'>w S</span>**<span style='color:#7f0055'>tud</span>**<span style='color:#393939'>ent();     </span>    <span style='color:#393939'>s.sho</span><span style='color:#6a3e3e'>w</span><span style='color:#393939'>();      </span>} <span style='color:#393939'>}</span>





**10. static关键字（静态）**

&emsp;static 是一个修饰符，是静态或者是全局的意思。可以修饰成员变量和成员方法



**10.1 概念**

static可以做什么：

&emsp;修饰**成员变量**：类变量，不属于对象，而是属于类。

&emsp;修饰**成员方法**：静态方法，储存在方法区的静态区

&emsp;修饰**代码块：**在class类文件加载到方法去的时候，进行对类进行初始化用的。



static修饰的成员方法和成员方法习惯上称为静态变量和静态方法

&emsp;调用方式：

&emsp;&emsp;类名.成员变量

&emsp;&emsp;类名.成员方法(..)



**10.2 static关键字特点**

&emsp;**1. 随着类的加载而加载**

&emsp;<span style='color:#df402a'>随着类的加载而将Static修饰的成员加载到方法区的静态区</span>

&emsp;**2. 优先于对象存在**

&emsp;<span style='color:#df402a'>只要class类文加载到方法区内，就算不调用，static修饰的方法和变量都会被提前初始化</span>

&emsp;**3. 被类的所有对象共享（只需要定义一份就可以了）**

&emsp;<span style='color:#df402a'>只要在一个对象定义一下就行了，其余的对象就不需要对这儿变量进行初始化了。！！！！！</span>

&emsp;这也是我们判断是否使用静态关键字的条件

&emsp;只有重复出现在不同对象的成员变量数据，才需要

&emsp;**4. 可以通过类名调用**

&emsp;//只要方法是static修饰的，就可以不通过new对象，直接就可以通过类名调用。

&emsp;//类中的static修饰的变量，都是提前初始化好了，可以直接用变量初始化的值。

**<span style='color:#7f0055'>class</span>** Person{     <span style='color:#3f7f5f'>// 使用static修饰成员变量</span>     **<span style='color:#7f0055'>private</span>** **<span style='color:#7f0055'>static</span>** String <span style='color:#0000c0'>country</span> = <span style='color:#2a00ff'>"中国"</span>;     **<span style='color:#7f0055'>public</span>** **<span style='color:#7f0055'>static</span>** **<span style='color:#7f0055'>void</span>** show(){         System.**<span style='color:#0000c0'>out</span>**.println(<span style='color:#0000c0'>country</span>);     } } **<span style='color:#7f0055'>class</span>** StaticDemo{     **<span style='color:#7f0055'>public</span>** **<span style='color:#7f0055'>static</span>** **<span style='color:#7f0055'>void</span>** main(String[] <span style='color:#6a3e3e'>args</span>){ <span style='color:#3f7f5f'>// show2方法是static修饰的，可以不new对象直接通过类名调用。</span> <span style='color:#3f7f5f'>// 类的static静态成员，优于对象而存在</span>         Person.show();<span style='color:#3f7f5f'>//country 大唐国</span>     } }

&emsp;**5. 静态区的变量，是可以变化的**

    <span style='color:#3f7f5f'>//static修饰的成员变量，一旦被修改，后面的其他对象中的country值也会修改</span>     Person p1 = **<span style='color:#7f0055'>new</span>** Person(<span style='color:#2a00ff'>"马云"</span>,50);     p1.show();<span style='color:#3f7f5f'>//country 中国</span>     <span style='color:#3f7f5f'>//给马化腾修改一下国籍</span>     Person p2 = **<span style='color:#7f0055'>new</span>** Person(<span style='color:#2a00ff'>"马化腾"</span>,<span style='color:#2a00ff'>"大唐国"</span>,45);     p2.show();<span style='color:#3f7f5f'>//country 大唐国</span>     Person p3 = **<span style='color:#7f0055'>new</span>** Person(<span style='color:#2a00ff'>"雷军"</span>,40);     p3.show();<span style='color:#3f7f5f'>//country 大唐国</span>



**10.3 static关键字注意事项**



&emsp;**1. 在静态方法中是没有this关键字的**

&emsp;<span style='color:#df402a'>this中的变量可能没有提前初始化，所以不能调用</span>

&emsp;**2. 静态方法只能访问静态的成员变量和静态的成员方法**

&emsp;<span style='color:#df402a'>因为要是用非静态变量和方法是没有被初始化的，</span>

&emsp;<span style='color:#df402a'>所以静态方法不能调用没被初始化的变量和方法</span>

&emsp;**3. static方法既可以用类直接调用，也可以直接new对象通过对象调用。**

<span style='color:#3f7f5f'>// show2方法是static修饰的，也可以new对象通过对象调用。</span> Person p1 = **<span style='color:#7f0055'>new</span>** Person(<span style='color:#2a00ff'>"马云"</span>,50); p1.show2();<span style='color:#3f7f5f'>//country 中国</span>

&emsp;**<span style='color:#df402a'>4. 要是其如果构造方法是（private）私有构造方法，那么只能直接调用，不能new对象方式来调用</span>**

&emsp;&emsp;**<span style='color:#df402a'>可以防止该类创建对象</span>**

&emsp;**<span style='color:#df402a'>5. 静态方法只能被重载，不能被重写</span>**

&emsp;&emsp;static、final、private方法本身都是编译期绑定的（也叫前期绑定）这些方法不存在多态



**10.4 使用场景**

&emsp;**静态变量**

&emsp;&emsp;在多个对象中共享变量

&emsp;&emsp;静态方法访问变量时

&emsp;**静态方法**

&emsp;&emsp;制作工具类时，方便调用



**10.5 静态变量和成员变量的区别**

**所属不同**

&emsp;静态变量属于类，所以也称为为<span style='color:#df402a'>类变量</span>

&emsp;成员变量属于对象，所以也称为<span style='color:#df402a'>实例变量(对象变量)</span>

**内存中位置不同**

&emsp;静态变量存储于方法区的静态区

&emsp;成员变量存储于堆内存

**内存出现时间不同**

&emsp;静态变量随着类的加载而加载，随着类的消失而消失

&emsp;成员变量随着对象的创建而存在，随着对象的消失而消失

**调用不同**

&emsp;<span style='color:#df402a'>静态变量可以通过类名调用，也可以通过对象调用</span>

&emsp;<span style='color:#df402a'>成员变量只能通过对象名调用</span>



**10.6 main方法解读**

    main方法解读

    public static void main(String[] args)

   

    public :访问权限修饰符

    static  :静态修饰符，修饰的成员不需要new对象就可以直接访问

    void    :无返回值，main方法是由JVM调用，JVM不需要返回值

    main    :jvm约定，只识别main方法

    args    :以前用于接收键盘录入的



**11 帮助文档**

**11.1 制作帮助文档**

**制作工具类**

&emsp;ArrayTools

**制作帮助文档步骤**

&emsp;添加文档注释

&emsp;&emsp;/** */

&emsp;&emsp;@author @param @return @version

&emsp;使用javadoc工具解析文档注释

&emsp;javadoc -d 目录 -author -version ArrayTools.java

**注意：**

源代码是否在一个文件中不重要，重要的是class文件在同一个文件夹下，就能调用。回顾之前的代码是否都是这样

编译时，会将相关联的两个class类一起编译（不管在不在一个java源文件中）

将printArray方法优化：加上static，不用new对象就直接可以调用，方便使用。

static修饰的printArray方法依然可以被人使用，直接在ArrayTools类中，定义私有的构造方法，这样就没法new对象了



**出现的问题：**

制作帮助文档出错

&emsp;找不到可以文档化的公共或受保护的类

&emsp;&emsp;权限不够，使用public修饰class类

演示ArrayTools文档的使用



**11.2 如何使用帮助文档**

找到CHM文档并打开

点击[显示]，找到[索引]，出现输入框

你应该知道你找谁?举例：Scanner

看这个类的结构(需不需要导包)

&emsp;成员变量 字段

&emsp;构造方法 构造方法

&emsp;成员方法 方法

看这个类的说明

看构造方法的说明

看成员方法的说明

然后使用



**11.3 根据文档编辑一个Math.random**

&emsp;<span style='color:#df402a'>公式：(数据类型)(最小值+Math.random()*(最大值-最小值+1))</span>

Math类概述

&emsp;Math包含用于执行基本数学运算的方法

Math类特点

&emsp;没有构造方法，因为成员都是静态的

Math类讲解一个方法

&emsp;获取随机数:public static double random()

&emsp;获取1-100之间的随机数



&emsp;Math.Random() :随机返回一个0<=x<100的double值

&emsp;**//随机1到100的随机值**

&emsp;(int)(Math.Random()+100)+1



**12 代码块**

&emsp;在Java中，使用{}括起来的代码被称为代码块，根据其位置和声明的不同，可以分为**<span style='color:#df402a'>局部代码块，构造代码块，静态代码块，同步代码块</span>**(多线程讲解)。



**12.1 局部代码块**



&emsp;解释：在方法中出现；限定变量生命周期，及早释放，提高内存利用率



&emsp;**出现位置：**在方法中出现

好**处：限**定变量生命周期，及早释放，提高内存利用率

注**意事项：**

&emsp;&emsp;1. 执行的顺序是按照代码顺序执行的

&emsp;&emsp;2. 不同的同级代码块直接的变量相互不影响，变量名可以相同

**<span style='color:#7f0055'>class</span>** <span style='color:#393939'>CodeDemo{</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>public</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>static</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>void</span>** <span style='color:#393939'>main(String[] </span><span style='color:#6a3e3e'>args</span><span style='color:#393939'>){</span>          <span style='color:#393939'> </span><span style='color:#3f7f5f'>//局部代码块：限定变量生命周期，及早释放，提高内存利用率</span>         <span style='color:#393939'>{</span>            <span style='color:#393939'> </span>**<span style='color:#7f0055'>int</span>**<span style='color:#393939'> </span><span style='color:#6a3e3e'>x</span> <span style='color:#393939'>= 10;   </span>             <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#6a3e3e'>x</span><span style='color:#393939'>);</span>         <span style='color:#393939'>}</span>        <span style='color:#393939'> </span><span style='color:#3f7f5f'>//局部代码块：限定变量生命周期，及早释放，提高内存利用率</span>         <span style='color:#393939'>{</span>            <span style='color:#393939'> </span>**<span style='color:#7f0055'>int</span>**<span style='color:#393939'> </span><span style='color:#6a3e3e'>x</span> <span style='color:#393939'>= 20;</span>             <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#6a3e3e'>x</span><span style='color:#393939'>);</span>         <span style='color:#393939'>}</span>     <span style='color:#393939'>}</span> <span style='color:#393939'>}</span>





**12.2 构造代码块**

&emsp;在类中方法外出现；多个构造方法中相同的代码存放到一起，<span style='color:#df402a'>每次调用构造都执行，并且在构造方法前执行</span>

&emsp;**出现位置：**在类中方法外出现

&emsp;**使用场景：**当多个构造方法中有相同的代码时，可以抽取到构造代码块中。

&emsp;**调用时机：**每次调用构造方法都执行，并且在构造方法前执行

&emsp;**注意事项：**

1：构造<span style='color:#df402a'>代码块比构造方法先执行，跟他们的位置无关</span>

2：多个构造代码块，它们的执行顺序就是代码的顺序

3：只有调用构造方法的时候，才会调用构造代码块，也就是只有new该类对象的时候，才调用

public class Code{ // 写在构造方法之前的构造代码块 { System.out.println("我是写在构造方法之前的构造代码块"); } // 构造方法 public Code(){ System.out.println("我是构造方法"); } // 写在构造方法之后的构造代码块 { System.out.println("我是写在构造方法之后的构造代码块"); } }





**12.3 静态代码块**

&emsp;一生只出现一次，只执行一次

&emsp;**出现位置：**在类中方法外出现，但是它是使用static修饰的。

使**用场景：需**要给类的静态成员初始化时使用。

**调用时机：在**类加载的时候就执行，并且只执行一次。

**<span style='color:#7f0055'>public</span>**<span style='color:#393939'> </span>**<span style='color:#7f0055'>class</span>** <span style='color:#393939'>Code{</span> <span style='color:#3f7f5f'>//静态代码块的加载时机：类加载的时候，类只会加载一次，所以静态代码块也只会加载一次。</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>static</span>**<span style='color:#393939'>{</span>         <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#2a00ff'>"我是Code静态代码块"</span><span style='color:#393939'>);</span>     <span style='color:#393939'>}</span>    <span style='color:#393939'> </span><span style='color:#3f7f5f'>// 写在构造方法之前的构造代码块</span>     <span style='color:#393939'>{</span>         <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#2a00ff'>"我是写在构造方法之前的构造代码块"</span><span style='color:#393939'>);</span>     <span style='color:#393939'>}</span>    <span style='color:#393939'> </span><span style='color:#3f7f5f'>// 构造方法</span>    <span style='color:#393939'> </span>**<span style='color:#7f0055'>public</span>** <span style='color:#393939'>Code(){</span>         <span style='color:#393939'>System.</span>**<span style='color:#0000c0'>out</span>**<span style='color:#393939'>.println(</span><span style='color:#2a00ff'>"我是构造方法"</span><span style='color:#393939'>);</span>     <span style='color:#393939'>}</span> <span style='color:#393939'>}</span>





**12.4 类执行顺序**

&emsp;**类的静态代码块**<span style='color:#df402a'>->构造代码块(mian方法不调用)</span>**->该类的main方法->**

&emsp;**调用类的静态代码块->(new对象后:->构造代码块->构造方法)**

&emsp;&emsp;&emsp;&emsp;&emsp;**->(又一次new该对象后:->构造代码块->构造方法)**

&emsp;**<span style='color:#df402a'>因为：构造代码块和构造方法只有在new对象的时候才调用，所以main所属的类不调用。</span>**







&emsp;**<span style='color:#df402a'>同一个级别内 是按照代码顺序从前往后执行</span>**

