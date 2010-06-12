//
//  TaskDetailsGeneral.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 16/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "TaskDetailsController.h"

@class CDTask;

@interface TaskDetailsGeneral : UIViewController <UITextFieldDelegate, UITextViewDelegate>
{
	CDTask *task;
	TaskDetailsController *parentCtrl;

	UITextField *subject;
	UILabel *descriptionLabel;
	UITextView *description;
	UIButton *categoriesButton;
	UILabel *priorityLabel;
	UITextField *priorityField;
}

@property (nonatomic, retain) IBOutlet UITextField *subject;
@property (nonatomic, retain) IBOutlet UILabel *descriptionLabel;
@property (nonatomic, retain) IBOutlet UITextView *description;
@property (nonatomic, retain) IBOutlet UIButton *categoriesButton;
@property (nonatomic, retain) IBOutlet UILabel *priorityLabel;
@property (nonatomic, retain) IBOutlet UITextField *priorityField;

- initWithTask:(CDTask *)task parent:(TaskDetailsController *)parent;

- (IBAction)onCategoriesClick:(UIButton *)button;

@end
