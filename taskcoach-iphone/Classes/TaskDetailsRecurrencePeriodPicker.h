//
//  TaskDetailsRecurrencePeriodPicker.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 12/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@class TaskDetailsRecurrencePeriodPicker;

@protocol TaskDetailsRecurrencePeriodPickerDelegate

- (void)recurrencePeriodPicker:(TaskDetailsRecurrencePeriodPicker *)picker didConfirm:(NSInteger)value;
- (void)recurrencePeriodPickerdidCancel:(TaskDetailsRecurrencePeriodPicker *)picker;

@end

@interface TaskDetailsRecurrencePeriodPicker : UIViewController
{
	UIPickerView *picker;
	id <TaskDetailsRecurrencePeriodPickerDelegate> delegate;
}

@property (nonatomic, retain) IBOutlet UIPickerView *picker;

- init;

- (void)setDelegate:(id <TaskDetailsRecurrencePeriodPickerDelegate>)delegate;
- (void)setSelection:(NSInteger)sel;

- (IBAction)onCancel:(UIButton *)button;
- (IBAction)onConfirm:(UIButton *)button;

@end
