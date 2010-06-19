//
//  TaskDetailsRecurrenceControlleriPad.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@class CDTask;
@class DatePickerViewController;

@interface TaskDetailsRecurrenceControlleriPad : UIViewController <UITextFieldDelegate>
{
	CDTask *task;

	UILabel *mainLabel;
	UISwitch *recurrenceSwitch;
	UITextField *amountField;
	UIButton *periodButton;
	UILabel *sameWeekdayLabel;
	UISwitch *sameWeekdaySwitch;
}

@property (nonatomic, retain) IBOutlet UILabel *mainLabel;
@property (nonatomic, retain) IBOutlet UISwitch *recurrenceSwitch;
@property (nonatomic, retain) IBOutlet UITextField *amountField;
@property (nonatomic, retain) IBOutlet UIButton *periodButton;
@property (nonatomic, retain) IBOutlet UILabel *sameWeekdayLabel;
@property (nonatomic, retain) IBOutlet UISwitch *sameWeekdaySwitch;

- initWithTask:(CDTask *)task;

- (IBAction)onRecurrenceChanged:(UISwitch *)_switch;
- (IBAction)onPeriodChanged:(UIButton *)button;
- (IBAction)onSameWeekdayChanged:(UISwitch *)_switch;

@end
