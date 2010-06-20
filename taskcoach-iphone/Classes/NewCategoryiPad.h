//
//  NewCategoryiPad.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 20/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface NewCategoryiPad : UIViewController <UITextFieldDelegate>
{
	UITextField *categoryName;
	UIButton *okButton;
	NSString *name;

	id target;
	SEL action;
}

@property (nonatomic, retain) IBOutlet UITextField *categoryName;
@property (nonatomic, retain) IBOutlet UIButton *okButton;

- initWithString:(NSString *)string target:(id)target action:(SEL)action;

- (IBAction)onClickOK:(UIButton *)button;

@end
