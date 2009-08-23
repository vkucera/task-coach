//
//  StringChoiceController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>


@interface StringChoiceController : UIViewController
{
	UITextField *textField;

	NSString *placeholder;
	NSString *text;

	id target;
	SEL action;
}

@property (nonatomic, retain) IBOutlet UITextField *textField;

- initWithPlaceholder:(NSString *)placeholder text:(NSString *)text target:(id)target action:(SEL)action;

- (IBAction)onCancel:(UIButton *)button;

@end
