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

	SimpleDatePicker *datePicker;
	UIPopoverController *popoverCtrl;
	NSString *dateName;
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

- initWithTask:(CDTask *)task;

- (IBAction)onClickDate:(UIButton *)button;
- (IBAction)incPriority:(UIButton *)button;
- (IBAction)decPriority:(UIButton *)button;

@end
