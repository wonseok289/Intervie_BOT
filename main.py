from openai import OpenAI
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import calendar
import json
import os
from datetime import datetime
import threading

# JSON 파일 경로
SCHEDULE_FILE = 'interview_schedule.json'

class InterviewAssistant:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="<Enter your API key here>",
        )
        
        self.messages = [{
            'role': 'system',
            'content': 'You are a helpful interview assistant. \
                        If you are given type of interview(ex: soccer club, AI graduate school), \
                        you say "OK, I\'m ready." and you are ready to assist the interview about given type.(Don\'t reply except "OK, I\'m ready.") \
                        And then whenever I ask you a question, you will ask the one interview question. \
                        If I reply to your question, you will evaluate my answer(점수: 1점 ~ 5점, ex: ★★★☆☆(3점)으로 표기 ) and give me the feedback. \
                        Or then whenever I ask you a tip, you will give me the tip about interview. \
                        And you must reply in Korean. \
                        '
        }]
        
        self.interview_ready = False
        self.setup_main_window()

    def setup_main_window(self):
        """메인 윈도우 설정"""
        self.root = tk.Tk()
        self.root.title("면접 어시스턴트")
        self.root.geometry("600x900")
        self.root.configure(bg='#f0f0f0')
        
        # 메인 프레임
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 타이틀
        title_label = tk.Label(main_frame, text="면접 어시스턴트", 
                              font=('Arial', 20, 'bold'), bg='#f0f0f0', fg='#333')
        title_label.pack(pady=10)
        
        # 면접 유형 입력 프레임
        self.setup_interview_type_frame(main_frame)
        
        # 메뉴 프레임
        self.setup_menu_frame(main_frame)
        
        # 상태 표시
        self.status_label = tk.Label(main_frame, text="면접 유형을 입력해주세요.", 
                                   font=('Arial', 12), bg='#f0f0f0', fg='#666')
        self.status_label.pack(pady=10)

    def setup_interview_type_frame(self, parent):
        """면접 유형 입력 프레임"""
        type_frame = tk.Frame(parent, bg='#f0f0f0')
        type_frame.pack(pady=20)
        
        tk.Label(type_frame, text="무슨 유형의 면접을 생각중이신가요?", 
                font=('Arial', 12), bg='#f0f0f0').pack(pady=5)
        
        self.interview_type_entry = tk.Entry(type_frame, font=('Arial', 12), width=30)
        self.interview_type_entry.pack(pady=5)
        self.interview_type_entry.bind('<Return>', self.set_interview_type)
        
        tk.Button(type_frame, text="설정", command=self.set_interview_type,
                 font=('Arial', 12), bg='#4CAF50', fg='white', width=10).pack(pady=5)

    def setup_menu_frame(self, parent):
        """메뉴 버튼 프레임"""
        self.menu_frame = tk.Frame(parent, bg='#f0f0f0')
        self.menu_frame.pack(pady=20)
        
        # 초기에는 비활성화
        self.menu_buttons = []
        
        buttons_info = [
            ("1. 모의면접", self.start_mock_interview, '#2196F3'),
            ("2. 면접 관련 팁", self.show_interview_tips, '#FF9800'),
            ("3. 면접 일정 예약", self.schedule_interview, '#9C27B0'),
            ("4. 면접 일정 확인", self.view_schedule, '#607D8B'),
            ("5. 나가기", self.quit_app, '#F44336')
        ]
        
        for text, command, color in buttons_info:
            btn = tk.Button(self.menu_frame, text=text, command=command,
                           font=('Arial', 12), bg=color, fg='white', 
                           width=20, height=2, state=tk.DISABLED)
            btn.pack(pady=5)
            self.menu_buttons.append(btn)

    def set_interview_type(self, event=None):
        """면접 유형 설정"""
        interview_type = self.interview_type_entry.get().strip()
        if not interview_type:
            messagebox.showwarning("경고", "면접 유형을 입력해주세요.")
            return
        
        self.status_label.config(text="설정 중...")
        self.interview_type_entry.config(state=tk.DISABLED)
        
        # API 호출을 별도 스레드에서 실행
        threading.Thread(target=self._process_interview_type, args=(interview_type,), daemon=True).start()

    def _process_interview_type(self, interview_type):
        """면접 유형 처리 (백그라운드)"""
        try:
            self.messages.append({
                'role': 'user',
                'content': interview_type
            })
            
            completion = self.client.chat.completions.create(
                model="qwen/qwen3-14b:free",
                messages=self.messages
            )
            self.messages.append(completion.choices[0].message)
            
            # UI 업데이트는 메인 스레드에서
            self.root.after(0, self._update_ui_after_setup, completion.choices[0].message.content)
            
        except Exception as e:
            self.root.after(0, self._handle_setup_error, str(e))

    def _update_ui_after_setup(self, response):
        """설정 완료 후 UI 업데이트"""
        self.interview_ready = True
        self.status_label.config(text=f"설정 완료: {response}")
        
        # 메뉴 버튼 활성화
        for btn in self.menu_buttons:
            btn.config(state=tk.NORMAL)

    def _handle_setup_error(self, error):
        """설정 오류 처리"""
        messagebox.showerror("오류", f"설정 중 오류가 발생했습니다: {error}")
        self.status_label.config(text="면접 유형을 다시 입력해주세요.")
        self.interview_type_entry.config(state=tk.NORMAL)

    def start_mock_interview(self):
        """모의면접 시작"""
        if not self.interview_ready:
            messagebox.showwarning("경고", "먼저 면접 유형을 설정해주세요.")
            return
        
        self.open_mock_interview_window()

    def open_mock_interview_window(self):
        """모의면접 윈도우 열기"""
        interview_window = tk.Toplevel(self.root)
        interview_window.title("모의면접")
        interview_window.geometry("700x600")
        interview_window.configure(bg='#f0f0f0')
        
        # 질문 표시 영역
        question_frame = tk.Frame(interview_window, bg='#f0f0f0')
        question_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(question_frame, text="면접 질문 & 답변", 
                font=('Arial', 14, 'bold'), bg='#f0f0f0').pack(anchor=tk.W)
        
        self.interview_text = scrolledtext.ScrolledText(question_frame, 
                                                       font=('Arial', 11), 
                                                       height=20, 
                                                       wrap=tk.WORD)
        self.interview_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 답변 입력 영역
        input_frame = tk.Frame(interview_window, bg='#f0f0f0')
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame, text="답변:", font=('Arial', 12), bg='#f0f0f0').pack(anchor=tk.W)
        
        self.answer_entry = tk.Text(input_frame, font=('Arial', 11), height=3)
        self.answer_entry.pack(fill=tk.X, pady=5)
        self.answer_entry.bind('<Control-Return>', lambda e: self.submit_answer())
        
        # 버튼 프레임
        button_frame = tk.Frame(interview_window, bg='#f0f0f0')
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(button_frame, text="새 질문", command=self.get_new_question,
                 font=('Arial', 12), bg='#2196F3', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="답변 제출", command=self.submit_answer,
                 font=('Arial', 12), bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="닫기", command=interview_window.destroy,
                 font=('Arial', 12), bg='#F44336', fg='white').pack(side=tk.RIGHT, padx=5)
        
        # 첫 질문 자동 생성
        self.current_interview_window = interview_window
        self.get_new_question()

    def get_new_question(self):
        """새 면접 질문 받기"""
        self.interview_text.insert(tk.END, "\n질문을 생성하는 중...\n")
        self.interview_text.see(tk.END)
        
        threading.Thread(target=self._get_question_background, daemon=True).start()

    def _get_question_background(self):
        """질문 생성 (백그라운드)"""
        try:
            self.messages.append({
                'role': 'user',
                'content': 'Give me one interview question.'
            })
            
            completion = self.client.chat.completions.create(
                model="qwen/qwen3-14b:free",
                messages=self.messages
            )
            self.messages.append(completion.choices[0].message)
            
            self.root.after(0, self._display_question, completion.choices[0].message.content)
            
        except Exception as e:
            self.root.after(0, self._handle_question_error, str(e))

    def _display_question(self, question):
        """질문 표시"""
        self.interview_text.delete("end-2l", tk.END)
        self.interview_text.insert(tk.END, f"Q. {question}\n\n")
        self.interview_text.see(tk.END)

    def _handle_question_error(self, error):
        """질문 생성 오류 처리"""
        self.interview_text.delete("end-2l", tk.END)
        self.interview_text.insert(tk.END, f"오류: {error}\n\n")
        self.interview_text.see(tk.END)

    def submit_answer(self):
        """답변 제출"""
        answer = self.answer_entry.get("1.0", tk.END).strip()
        if not answer:
            messagebox.showwarning("경고", "답변을 입력해주세요.")
            return
        
        self.interview_text.insert(tk.END, f"A. {answer}\n\n")
        self.interview_text.insert(tk.END, "평가 중...\n")
        self.interview_text.see(tk.END)
        
        self.answer_entry.delete("1.0", tk.END)
        
        threading.Thread(target=self._evaluate_answer_background, args=(answer,), daemon=True).start()

    def _evaluate_answer_background(self, answer):
        """답변 평가 (백그라운드)"""
        try:
            self.messages.append({
                'role': 'user',
                'content': answer
            })
            
            completion = self.client.chat.completions.create(
                model="qwen/qwen3-14b:free",
                messages=self.messages
            )
            self.messages.append(completion.choices[0].message)
            
            self.root.after(0, self._display_evaluation, completion.choices[0].message.content)
            
        except Exception as e:
            self.root.after(0, self._handle_evaluation_error, str(e))

    def _display_evaluation(self, evaluation):
        """평가 결과 표시"""
        self.interview_text.delete("end-2l", tk.END)
        self.interview_text.insert(tk.END, f"평가: {evaluation}\n\n")
        self.interview_text.insert(tk.END, "-" * 50 + "\n\n")
        self.interview_text.see(tk.END)

    def _handle_evaluation_error(self, error):
        """평가 오류 처리"""
        self.interview_text.delete("end-2l", tk.END)
        self.interview_text.insert(tk.END, f"평가 오류: {error}\n\n")
        self.interview_text.see(tk.END)

    def show_interview_tips(self):
        """면접 팁 보기"""
        if not self.interview_ready:
            messagebox.showwarning("경고", "먼저 면접 유형을 설정해주세요.")
            return
        
        tips_window = tk.Toplevel(self.root)
        tips_window.title("면접 팁")
        tips_window.geometry("600x500")
        tips_window.configure(bg='#f0f0f0')
        
        tk.Label(tips_window, text="면접 팁", 
                font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=10)
        
        tips_text = scrolledtext.ScrolledText(tips_window, 
                                             font=('Arial', 11), 
                                             wrap=tk.WORD)
        tips_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tips_text.insert(tk.END, "팁을 불러오는 중...\n")
        
        tk.Button(tips_window, text="닫기", command=tips_window.destroy,
                 font=('Arial', 12), bg='#F44336', fg='white').pack(pady=10)
        
        # 팁 가져오기
        threading.Thread(target=self._get_tips_background, args=(tips_text,), daemon=True).start()

    def _get_tips_background(self, tips_text):
        """팁 가져오기 (백그라운드)"""
        try:
            messages_copy = self.messages.copy()
            messages_copy.append({
                'role': 'user',
                'content': 'Give me helpful tips for interview'
            })
            
            completion = self.client.chat.completions.create(
                model="qwen/qwen3-14b:free",
                messages=messages_copy
            )
            
            self.root.after(0, self._display_tips, tips_text, completion.choices[0].message.content)
            
        except Exception as e:
            self.root.after(0, self._handle_tips_error, tips_text, str(e))

    def _display_tips(self, tips_text, tips):
        """팁 표시"""
        tips_text.delete("1.0", tk.END)
        tips_text.insert(tk.END, tips)

    def _handle_tips_error(self, tips_text, error):
        """팁 오류 처리"""
        tips_text.delete("1.0", tk.END)
        tips_text.insert(tk.END, f"오류: {error}")

    def schedule_interview(self):
        """면접 일정 예약"""
        self.open_calendar()

    def open_calendar(self):
        """달력 GUI 열기"""
        self.selected_date = None
        
        def on_date_select(day):
            self.selected_date = f"{current_year}-{current_month:02d}-{day:02d}"
            calendar_window.destroy()
            self.add_schedule_detail()
        
        def prev_month():
            nonlocal current_month, current_year
            current_month -= 1
            if current_month < 1:
                current_month = 12
                current_year -= 1
            update_calendar()
        
        def next_month():
            nonlocal current_month, current_year
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
            update_calendar()
        
        def update_calendar():
            for widget in calendar_frame.winfo_children():
                widget.destroy()
            
            month_label.config(text=f"{current_year}년 {current_month}월")
            
            days = ['월', '화', '수', '목', '금', '토', '일']
            for i, day in enumerate(days):
                tk.Label(calendar_frame, text=day, font=('Arial', 10, 'bold')).grid(row=0, column=i, padx=2, pady=2)
            
            cal = calendar.monthcalendar(current_year, current_month)
            for week_num, week in enumerate(cal, 1):
                for day_num, day in enumerate(week):
                    if day == 0:
                        tk.Label(calendar_frame, text="", width=4, height=2).grid(row=week_num, column=day_num, padx=1, pady=1)
                    else:
                        btn = tk.Button(calendar_frame, text=str(day), width=4, height=2,
                                      command=lambda d=day: on_date_select(d))
                        btn.grid(row=week_num, column=day_num, padx=1, pady=1)
        
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        
        calendar_window = tk.Toplevel(self.root)
        calendar_window.title("면접 일정 선택")
        calendar_window.geometry("400x350")
        calendar_window.configure(bg='#f0f0f0')
        
        # 월 네비게이션
        nav_frame = tk.Frame(calendar_window, bg='#f0f0f0')
        nav_frame.pack(pady=10)
        
        tk.Button(nav_frame, text="◀", command=prev_month, font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        month_label = tk.Label(nav_frame, text="", font=('Arial', 12, 'bold'), bg='#f0f0f0')
        month_label.pack(side=tk.LEFT, padx=20)
        tk.Button(nav_frame, text="▶", command=next_month, font=('Arial', 12)).pack(side=tk.LEFT, padx=5)
        
        # 달력 프레임
        calendar_frame = tk.Frame(calendar_window, bg='#f0f0f0')
        calendar_frame.pack(pady=10)
        
        update_calendar()
        
        tk.Button(calendar_window, text="취소", command=calendar_window.destroy,
                 font=('Arial', 12), bg='#F44336', fg='white').pack(pady=10)

    def add_schedule_detail(self):
        """일정 세부사항 추가"""
        if not self.selected_date:
            return
        
        detail_window = tk.Toplevel(self.root)
        detail_window.title("일정 세부사항 입력")
        detail_window.geometry("400x300")
        detail_window.configure(bg='#f0f0f0')
        
        tk.Label(detail_window, text=f"선택된 날짜: {self.selected_date}", 
                font=('Arial', 12, 'bold'), bg='#f0f0f0').pack(pady=10)
        
        tk.Label(detail_window, text="면접 일정의 세부사항을 입력해주세요:", 
                font=('Arial', 12), bg='#f0f0f0').pack(pady=5)
        
        detail_text = tk.Text(detail_window, font=('Arial', 11), height=8)
        detail_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        def save_schedule():
            schedule_detail = detail_text.get("1.0", tk.END).strip()
            if not schedule_detail:
                messagebox.showwarning("경고", "일정 세부사항을 입력해주세요.")
                return
            
            schedules = self.load_schedule()
            if self.selected_date not in schedules:
                schedules[self.selected_date] = []
            schedules[self.selected_date].append(schedule_detail)
            
            self.save_schedule(schedules)
            messagebox.showinfo("완료", f"일정이 저장되었습니다!\n{self.selected_date} - {schedule_detail}")
            detail_window.destroy()
        
        button_frame = tk.Frame(detail_window, bg='#f0f0f0')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="저장", command=save_schedule,
                 font=('Arial', 12), bg='#4CAF50', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="취소", command=detail_window.destroy,
                 font=('Arial', 12), bg='#F44336', fg='white').pack(side=tk.LEFT, padx=5)

    def view_schedule(self):
        """일정 확인"""
        schedules = self.load_schedule()
        
        schedule_window = tk.Toplevel(self.root)
        schedule_window.title("면접 일정 확인")
        schedule_window.geometry("500x600")
        schedule_window.configure(bg='#f0f0f0')
        
        tk.Label(schedule_window, text="면접 일정 목록", 
                font=('Arial', 16, 'bold'), bg='#f0f0f0').pack(pady=10)
        
        schedule_text = scrolledtext.ScrolledText(schedule_window, 
                                                 font=('Arial', 11), 
                                                 wrap=tk.WORD)
        schedule_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        if not schedules:
            schedule_text.insert(tk.END, "저장된 면접 일정이 없습니다.")
        else:
            sorted_dates = sorted(schedules.keys())
            for date in sorted_dates:
                schedule_text.insert(tk.END, f"📅 {date}\n")
                for i, detail in enumerate(schedules[date], 1):
                    schedule_text.insert(tk.END, f"  {i}. {detail}\n")
                schedule_text.insert(tk.END, "\n")
        
        tk.Button(schedule_window, text="닫기", command=schedule_window.destroy,
                 font=('Arial', 12), bg='#F44336', fg='white').pack(pady=10)

    def load_schedule(self):
        """JSON 파일에서 일정 불러오기"""
        if os.path.exists(SCHEDULE_FILE):
            try:
                with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_schedule(self, schedule_data):
        """JSON 파일에 일정 저장하기"""
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=2)

    def quit_app(self):
        """앱 종료"""
        if messagebox.askyesno("종료", "정말로 종료하시겠습니까?"):
            self.root.quit()

    def run(self):
        """앱 실행"""
        self.root.mainloop()

if __name__ == "__main__":
    app = InterviewAssistant()
    app.run()