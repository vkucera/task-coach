//
//  TaskDetailsController-iPad.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CDTask;
@class SimpleDatePicker;
@class TaskCategoryPickerController;
@class TaskDetailsEffortsBase;

@interface TaskDetailsControlleriPad : UIViewController <UITextFieldDelegate, UITextViewDelegate, UIPopoverControllerDelegate>
{
	CDTask *task;

	UITextField *subject;
	UITextView *description;

	UIButton *startDateButton;
	UIButton *dueDateButton;
	UIButton *completionDateButton;
	UIButton *reminderDateButton;
	UILabel *priorityLabel;
	UIButton *recurrenceButton;
	UIButton *effortButton;
	UIButton *categoryButton;
	UISlider *prioritySlider;

	SimpleDatePicker *datePicker;
	UIPopoverController *popoverCtrl;
	NSString *dateName;
	TaskCategoryPickerController *taskCatCtrl;
	TaskDetailsEffortsBase *taskEffortCtrl;
}

@property (nonatomic, retain) IBOutlet UITextField *subject;
@property (nonatomic, retain) IBOutlet UITextView *description;

@property (nonatomic, retain) IBOutlet UIButton *startDateButton;
@property (nonatomic, retain) IBOutlet UIButton *dueDateButton;
@property (nonatomic, retain) IBOutlet UIButton *completionDateButton;
@property (nonatomic, retain) IBOutlet UIButton *reminderDateButton;
@property (nonatomic, retain) IBOutlet UILabel *priorityLabel;
@property (nonatomic, retain) IBOutlet UIButton *recurrenceButton;
@property (nonatomic, retain) IBOutlet UIButton *effortButton;
@property (nonatomic, retain) IBOutlet UIButton *categoryButton;
@property (nonatomic, retain) IBOutlet UISlider *prioritySlider;

@property (nonatomic, retain) IBOutlet TaskCategoryPickerController *taskCatCtrl;
@property (nonatomic, retain) IBOutlet TaskDetailsEffortsBase *taskEffortCtrl;

- initWithTask:(CDTask *)task;

- (IBAction)onClickDate:(UIButton *)button;
- (IBAction)onClickEffort:(UIButton *)button;
- (IBAction)onClickRecurrence:(UIButton *)button;
- (IBAction)onPriorityChanged:(UISlider *)slider;
- (IBAction)onPickCategories:(UIButton *)button;

@end
