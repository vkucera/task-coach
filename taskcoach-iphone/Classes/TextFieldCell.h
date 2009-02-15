//
//  TextFieldCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface TextFieldCell : UITableViewCell
{
	UITextField *textField;
}

@property (nonatomic, retain) IBOutlet UITextField *textField;

@end
